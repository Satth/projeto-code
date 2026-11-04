"""Prova de que o serviço funciona sem SQLite.

O ``ServicoEstoque`` depende apenas da porta ``RepositorioEstoquePorta``.
A implementação abaixo mantém os dados em memória e atende ao mesmo
contrato, sem importar ``sqlite3`` nem a infraestrutura concreta.
"""

from estoque.aplicacao.modelos import MovimentacaoRegistrada, ProdutoComId
from estoque.aplicacao.portas import RepositorioEstoquePorta
from estoque.aplicacao.servico import ServicoEstoque
from estoque.dominio.erros import (
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
    SaldoDesatualizado,
)
from estoque.dominio.produto import Produto
from estoque.infraestrutura.sqlite.repositorio import RepositorioEstoque


def _clonar(produto):
    return Produto(
        produto.nome,
        produto.preco_unitario,
        produto.quantidade,
        produto.quantidade_minima,
    )


class RepositorioSimulado:
    """Implementação em memória do contrato usado pela aplicação."""

    def __init__(self):
        self._produtos = {}
        self._proximo_id = 1
        self._movimentacoes = []
        self._proximo_registro = 1

    def salvar(self, produto):
        produto_id = self._proximo_id
        self._proximo_id += 1
        self._produtos[produto_id] = _clonar(produto)
        return produto_id

    def buscar(self, produto_id):
        produto = self._produtos.get(produto_id)
        return None if produto is None else _clonar(produto)

    def listar(self):
        return [
            ProdutoComId(produto_id, _clonar(produto))
            for produto_id, produto in sorted(self._produtos.items())
        ]

    def existe_nome(self, nome, exceto_id=None):
        return any(
            produto.nome.casefold() == nome.casefold() and produto_id != exceto_id
            for produto_id, produto in self._produtos.items()
        )

    def atualizar(self, produto_id, produto):
        if produto_id not in self._produtos:
            return False
        self._produtos[produto_id] = _clonar(produto)
        return True

    def remover(self, produto_id):
        if produto_id not in self._produtos:
            return False
        if any(
            registro.produto_id == produto_id
            for registro in self._movimentacoes
        ):
            raise ProdutoComMovimentacoes(
                "o produto possui movimentações e não pode ser removido"
            )
        del self._produtos[produto_id]
        return True

    def aplicar_movimentacao(
        self,
        produto_id,
        quantidade_anterior,
        nova_quantidade,
        tipo,
        quantidade,
        observacao,
    ):
        produto = self._produtos.get(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado(f"produto {produto_id} não encontrado")
        if produto.quantidade != quantidade_anterior:
            raise SaldoDesatualizado(
                f"o saldo do produto {produto_id} mudou durante a operação"
            )

        produto.ajustar(nova_quantidade)
        self._movimentacoes.append(
            MovimentacaoRegistrada(
                id=self._proximo_registro,
                produto_id=produto_id,
                produto_nome=produto.nome,
                tipo=tipo,
                quantidade=quantidade,
                quantidade_anterior=quantidade_anterior,
                quantidade_nova=nova_quantidade,
                observacao=observacao,
                criado_em="2026-01-01T00:00:00.000Z",
            )
        )
        self._proximo_registro += 1

    def listar_movimentacoes(self, produto_id=None):
        if produto_id is None:
            return list(self._movimentacoes)
        return [
            registro
            for registro in self._movimentacoes
            if registro.produto_id == produto_id
        ]


def test_repositorio_simulado_atende_ao_contrato_da_aplicacao():
    assert isinstance(RepositorioSimulado(), RepositorioEstoquePorta)


def test_repositorio_sqlite_atende_ao_contrato_da_aplicacao(conexao):
    assert isinstance(RepositorioEstoque(conexao), RepositorioEstoquePorta)


def test_servico_executa_casos_de_uso_com_repositorio_simulado():
    repositorio = RepositorioSimulado()
    servico = ServicoEstoque(repositorio)

    teclado = servico.cadastrar("Teclado", "150.00", 10, 5)
    servico.cadastrar("Mouse", "80.00", 2, 5)

    assert servico.buscar(teclado.id).nome == "Teclado"
    assert [item.nome for item in servico.listar()] == ["Teclado", "Mouse"]

    entrada = servico.dar_entrada(teclado.id, 5, "compra")
    assert entrada.quantidade == 15

    saida = servico.dar_saida(teclado.id, 3, "venda")
    assert saida.quantidade == 12

    ajustado = servico.ajustar(teclado.id, 4, "inventário")
    assert ajustado.quantidade == 4

    historico = servico.historico(teclado.id)
    assert [registro.tipo for registro in historico] == [
        "entrada",
        "saida",
        "ajuste",
    ]
    assert [registro.quantidade_anterior for registro in historico] == [10, 15, 12]
    assert [registro.quantidade_nova for registro in historico] == [15, 12, 4]

    assert [item.nome for item in servico.abaixo_do_minimo()] == [
        "Teclado",
        "Mouse",
    ]

    atualizado = servico.atualizar(teclado.id, "Teclado ABNT", "160.00", 3)
    assert atualizado.nome == "Teclado ABNT"
    assert atualizado.quantidade == 4


def test_servico_recusa_saldo_desatualizado_no_repositorio_simulado():
    class RepositorioComCorrida(RepositorioSimulado):
        def buscar(self, produto_id):
            produto = super().buscar(produto_id)
            if produto is not None:
                self._produtos[produto_id].ajustar(99)
            return produto

    repositorio = RepositorioComCorrida()
    servico = ServicoEstoque(repositorio)
    item = servico.cadastrar("Teclado", "150.00", 10, 5)

    try:
        servico.dar_entrada(item.id, 1)
    except SaldoDesatualizado:
        pass
    else:
        raise AssertionError("o saldo desatualizado deveria ser recusado")

    assert servico.historico(item.id) == []


def test_servico_recusa_remocao_com_historico_no_repositorio_simulado():
    repositorio = RepositorioSimulado()
    servico = ServicoEstoque(repositorio)
    item = servico.cadastrar("Teclado", "150.00", 10, 5)
    servico.dar_entrada(item.id, 1)

    try:
        servico.remover(item.id)
    except ProdutoComMovimentacoes:
        pass
    else:
        raise AssertionError("a remoção com histórico deveria ser recusada")

    assert servico.buscar(item.id).quantidade == 11
