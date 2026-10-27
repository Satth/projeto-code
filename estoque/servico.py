"""Regras de negócio do estoque, independentes de detalhes do SQLite.

O serviço recebe um repositório pronto. Ele não importa ``sqlite3`` nem
monta SQL; apenas coordena as validações do domínio e as operações de
persistência.
"""

from .erros import NomeDuplicado, ProdutoNaoEncontrado
from .movimentacao import Ajuste, Entrada, Saida
from .produto import Produto
from .repositorio import ProdutoComId


class ServicoEstoque:
    """Coordena produtos e movimentações sobre um repositório."""

    def __init__(self, repositorio):
        self._repositorio = repositorio

    def cadastrar(
        self,
        nome,
        preco_unitario,
        quantidade=0,
        quantidade_minima=0,
    ):
        """Cadastra um produto. A quantidade informada é o saldo inicial."""
        produto = Produto(
            nome=nome,
            preco_unitario=preco_unitario,
            quantidade=quantidade,
            quantidade_minima=quantidade_minima,
        )
        if self._repositorio.existe_nome(produto.nome):
            raise NomeDuplicado(f"já existe um produto chamado {produto.nome}")

        produto_id = self._repositorio.salvar(produto)
        return ProdutoComId(produto_id, produto)

    def listar(self):
        """Lista todos os produtos cadastrados."""
        return self._repositorio.listar()

    def buscar(self, produto_id):
        """Busca um produto ou levanta ``ProdutoNaoEncontrado``."""
        return ProdutoComId(produto_id, self._obter(produto_id))

    def atualizar(
        self,
        produto_id,
        nome,
        preco_unitario,
        quantidade_minima,
    ):
        """Atualiza nome, preço e mínimo, preservando o saldo atual."""
        produto = self._obter(produto_id)
        produto.nome = nome
        produto.preco_unitario = preco_unitario
        produto.quantidade_minima = quantidade_minima

        if self._repositorio.existe_nome(produto.nome, exceto_id=produto_id):
            raise NomeDuplicado(f"já existe um produto chamado {produto.nome}")

        if not self._repositorio.atualizar(produto_id, produto):
            raise ProdutoNaoEncontrado(f"produto {produto_id} não encontrado")

        return ProdutoComId(produto_id, produto)

    def remover(self, produto_id):
        """Remove um produto. O histórico impede a remoção."""
        if not self._repositorio.remover(produto_id):
            raise ProdutoNaoEncontrado(f"produto {produto_id} não encontrado")

    def dar_entrada(self, produto_id, quantidade, observacao=""):
        """Registra uma entrada de estoque."""
        return self._movimentar(produto_id, Entrada(quantidade, observacao))

    def dar_saida(self, produto_id, quantidade, observacao=""):
        """Registra uma saída, recusando quantidade acima do disponível."""
        return self._movimentar(produto_id, Saida(quantidade, observacao))

    def ajustar(self, produto_id, nova_quantidade, observacao=""):
        """Ajusta o saldo para uma quantidade absoluta."""
        return self._movimentar(
            produto_id, Ajuste(nova_quantidade, observacao)
        )

    def historico(self, produto_id=None):
        """Devolve as movimentações, opcionalmente filtradas por produto."""
        if produto_id is not None:
            self._obter(produto_id)
        return self._repositorio.listar_movimentacoes(produto_id)

    def abaixo_do_minimo(self):
        """Lista os produtos cujo saldo está abaixo do mínimo."""
        return [
            item for item in self.listar() if item.produto.abaixo_do_minimo()
        ]

    def _obter(self, produto_id):
        produto = self._repositorio.buscar(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado(f"produto {produto_id} não encontrado")
        return produto

    def _movimentar(self, produto_id, movimentacao):
        """Aplica a movimentação e persiste saldo + histórico juntos."""
        produto = self._obter(produto_id)
        quantidade_anterior = produto.quantidade

        # Chamada polimórfica: Entrada, Saida e Ajuste implementam aplicar().
        movimentacao.aplicar(produto)

        self._repositorio.aplicar_movimentacao(
            produto_id=produto_id,
            quantidade_anterior=quantidade_anterior,
            nova_quantidade=produto.quantidade,
            tipo=movimentacao.tipo,
            quantidade=movimentacao.quantidade,
            observacao=movimentacao.observacao,
        )
        return ProdutoComId(produto_id, produto)
