"""Operações de leitura e escrita no SQLite.

O repositório sabe gravar e consultar registros. Ele valida os
parâmetros recebidos na fronteira do banco e traduz os erros de
integridade; as regras de negócio continuam no domínio e no serviço.
"""

import sqlite3
from dataclasses import dataclass
from decimal import Decimal

from .erros import (
    EstoqueInsuficiente,
    MovimentacaoInconsistente,
    NomeDuplicado,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
    SaldoDesatualizado,
)
from .produto import Produto
from .validacao import (
    validar_inteiro,
    validar_observacao,
    validar_quantidade_positiva,
    validar_tipo_movimentacao,
)

CAMPOS_PRODUTO = "id, nome, preco_unitario, quantidade, quantidade_minima"


@dataclass(frozen=True)
class ProdutoComId:
    """Produto do domínio acompanhado do identificador gerado pelo banco."""

    id: int
    produto: Produto

    @property
    def nome(self):
        return self.produto.nome

    @property
    def quantidade(self):
        return self.produto.quantidade


@dataclass(frozen=True)
class MovimentacaoRegistrada:
    """Uma linha do histórico, já convertida para um objeto legível."""

    id: int
    produto_id: int
    produto_nome: str
    tipo: str
    quantidade: int
    quantidade_anterior: int
    quantidade_nova: int
    observacao: str
    criado_em: str


def _linha_para_produto(linha):
    return Produto(
        nome=linha["nome"],
        preco_unitario=Decimal(linha["preco_unitario"]),
        quantidade=linha["quantidade"],
        quantidade_minima=linha["quantidade_minima"],
    )


class RepositorioEstoque:
    """Traduz entre os objetos de domínio e as tabelas SQLite."""

    def __init__(self, conexao):
        self._conexao = conexao

    def salvar(self, produto):
        """Insere um produto e devolve o id gerado."""
        try:
            with self._conexao:
                cursor = self._conexao.execute(
                    """
                    INSERT INTO produtos
                        (nome, preco_unitario, quantidade, quantidade_minima)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        produto.nome,
                        str(produto.preco_unitario),
                        produto.quantidade,
                        produto.quantidade_minima,
                    ),
                )
                if cursor.lastrowid is None:
                    raise RuntimeError("o SQLite não devolveu o id do produto")
                return cursor.lastrowid
        except sqlite3.IntegrityError as erro:
            if "UNIQUE" in str(erro).upper():
                raise NomeDuplicado(
                    f"já existe um produto chamado {produto.nome}"
                ) from erro
            raise

    def buscar(self, produto_id):
        """Devolve um ``Produto`` ou ``None`` quando o id não existe."""
        linha = self._conexao.execute(
            f"SELECT {CAMPOS_PRODUTO} FROM produtos WHERE id = ?",
            (produto_id,),
        ).fetchone()
        return None if linha is None else _linha_para_produto(linha)

    def listar(self):
        """Lista os produtos em ordem de cadastro."""
        linhas = self._conexao.execute(
            f"SELECT {CAMPOS_PRODUTO} FROM produtos ORDER BY id"
        ).fetchall()
        return [
            ProdutoComId(linha["id"], _linha_para_produto(linha))
            for linha in linhas
        ]

    def existe_nome(self, nome, exceto_id=None):
        """Verifica a unicidade do nome, opcionalmente ignorando um id."""
        sql = "SELECT 1 FROM produtos WHERE nome = ? COLLATE NOCASE"
        parametros = [nome]
        if exceto_id is not None:
            sql += " AND id != ?"
            parametros.append(exceto_id)
        return self._conexao.execute(sql, parametros).fetchone() is not None

    def atualizar(self, produto_id, produto):
        """Atualiza os dados cadastrais, sem alterar o saldo em estoque.

        A quantidade só muda por ``aplicar_movimentacao``; isso evita que
        uma edição de cadastro apague o histórico de entradas e saídas.
        """
        try:
            with self._conexao:
                cursor = self._conexao.execute(
                    """
                    UPDATE produtos
                       SET nome = ?, preco_unitario = ?, quantidade_minima = ?
                     WHERE id = ?
                    """,
                    (
                        produto.nome,
                        str(produto.preco_unitario),
                        produto.quantidade_minima,
                        produto_id,
                    ),
                )
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as erro:
            if "UNIQUE" in str(erro).upper():
                raise NomeDuplicado(
                    f"já existe um produto chamado {produto.nome}"
                ) from erro
            raise

    def remover(self, produto_id):
        """Remove um produto sem movimentações, devolvendo se houve remoção."""
        try:
            with self._conexao:
                cursor = self._conexao.execute(
                    "DELETE FROM produtos WHERE id = ?", (produto_id,)
                )
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as erro:
            nome_erro = getattr(erro, "sqlite_errorname", "")
            if nome_erro in {
                "SQLITE_CONSTRAINT_FOREIGNKEY",
                "SQLITE_CONSTRAINT_TRIGGER",
            }:
                possui_historico = self._conexao.execute(
                    "SELECT 1 FROM movimentacoes WHERE produto_id = ?",
                    (produto_id,),
                ).fetchone()
                if possui_historico is not None:
                    raise ProdutoComMovimentacoes(
                        "o produto possui movimentações e não pode ser removido; "
                        "preserve o histórico ou remova as movimentações primeiro"
                    ) from erro
            raise

    def aplicar_movimentacao(
        self,
        produto_id,
        quantidade_anterior,
        nova_quantidade,
        tipo,
        quantidade,
        observacao,
    ):
        """Atualiza o saldo e grava o histórico na mesma transação.

        A atualização é condicional ao saldo lido pelo serviço. Se outro
        processo alterar o saldo antes desta gravação, nenhuma linha é
        atualizada e o histórico não é gravado. Se a gravação do histórico
        falhar, o ``with`` da conexão desfaz também a alteração de quantidade.
        """
        valores = self._validar_movimentacao(
            produto_id=produto_id,
            quantidade_anterior=quantidade_anterior,
            nova_quantidade=nova_quantidade,
            tipo=tipo,
            quantidade=quantidade,
            observacao=observacao,
        )

        with self._conexao:
            cursor = self._conexao.execute(
                """
                UPDATE produtos
                   SET quantidade = ?
                 WHERE id = ? AND quantidade = ?
                """,
                (
                    valores["quantidade_nova"],
                    valores["produto_id"],
                    valores["quantidade_anterior"],
                ),
            )
            if cursor.rowcount != 1:
                existe = self._conexao.execute(
                    "SELECT 1 FROM produtos WHERE id = ?",
                    (valores["produto_id"],),
                ).fetchone()
                if existe is None:
                    raise ProdutoNaoEncontrado(
                        f"produto {valores['produto_id']} não encontrado"
                    )
                raise SaldoDesatualizado(
                    f"o saldo do produto {valores['produto_id']} mudou durante "
                    "a operação; recarregue o produto e tente novamente"
                )
            self._registrar_movimentacao(**valores)

    @staticmethod
    def _validar_movimentacao(
        produto_id,
        quantidade_anterior,
        nova_quantidade,
        tipo,
        quantidade,
        observacao,
    ):
        """Valida e normaliza os valores antes de qualquer escrita."""
        produto_id = validar_inteiro(produto_id, "id do produto", minimo=1)
        quantidade_anterior = validar_inteiro(
            quantidade_anterior, "quantidade anterior"
        )
        nova_quantidade = validar_inteiro(nova_quantidade, "nova quantidade")
        tipo = validar_tipo_movimentacao(tipo)
        observacao = validar_observacao(observacao)

        if tipo == "ajuste":
            quantidade = validar_inteiro(quantidade, "quantidade do ajuste")
            if quantidade != nova_quantidade:
                raise MovimentacaoInconsistente(
                    "no ajuste, a quantidade informada deve ser igual ao novo saldo"
                )
        else:
            quantidade = validar_quantidade_positiva(
                quantidade, "quantidade da movimentação"
            )
            if tipo == "entrada":
                if nova_quantidade != quantidade_anterior + quantidade:
                    raise MovimentacaoInconsistente(
                        "entrada incoerente: o novo saldo deve ser a soma do "
                        "saldo anterior com a quantidade"
                    )
            else:
                if quantidade > quantidade_anterior:
                    raise EstoqueInsuficiente(
                        f"saída de {quantidade} maior que o saldo disponível "
                        f"{quantidade_anterior}"
                    )
                if nova_quantidade != quantidade_anterior - quantidade:
                    raise MovimentacaoInconsistente(
                        "saída incoerente: o novo saldo deve ser o saldo "
                        "anterior menos a quantidade"
                    )

        return {
            "produto_id": produto_id,
            "quantidade_anterior": quantidade_anterior,
            "quantidade_nova": nova_quantidade,
            "tipo": tipo,
            "quantidade": quantidade,
            "observacao": observacao,
        }

    def _registrar_movimentacao(
        self,
        produto_id,
        tipo,
        quantidade,
        quantidade_anterior,
        quantidade_nova,
        observacao,
    ):
        """Insere a linha do histórico. Separado para permitir teste de rollback."""
        self._conexao.execute(
            """
            INSERT INTO movimentacoes
                (produto_id, tipo, quantidade, quantidade_anterior,
                 quantidade_nova, observacao)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                produto_id,
                tipo,
                quantidade,
                quantidade_anterior,
                quantidade_nova,
                observacao,
            ),
        )

    def listar_movimentacoes(self, produto_id=None):
        """Devolve o histórico completo ou o de um produto específico."""
        sql = """
            SELECT m.id, m.produto_id, p.nome AS produto_nome, m.tipo,
                   m.quantidade, m.quantidade_anterior, m.quantidade_nova,
                   m.observacao, m.criado_em
              FROM movimentacoes AS m
              JOIN produtos AS p ON p.id = m.produto_id
        """
        parametros = []
        if produto_id is not None:
            sql += " WHERE m.produto_id = ?"
            parametros.append(produto_id)
        sql += " ORDER BY m.id"

        linhas = self._conexao.execute(sql, parametros).fetchall()
        return [MovimentacaoRegistrada(**dict(linha)) for linha in linhas]
