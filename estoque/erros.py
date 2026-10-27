"""Exceções de negócio do domínio de controle de estoque.

Erros esperados da aplicação herdam de ``ErroDeEstoque``. Assim, a
demonstração consegue tratar falhas de negócio sem capturar qualquer
``Exception`` genérica.
"""


class ErroDeEstoque(Exception):
    """Classe base para os erros esperados do domínio de estoque."""


class DadosInvalidos(ErroDeEstoque, ValueError):
    """Um dado informado não atende às regras do domínio."""


class EstoqueInsuficiente(ErroDeEstoque):
    """A quantidade solicitada é maior que o saldo disponível."""


class ProdutoNaoEncontrado(ErroDeEstoque):
    """O produto informado não existe."""


class NomeDuplicado(ErroDeEstoque):
    """Já existe um produto com o mesmo nome."""


class ProdutoComMovimentacoes(ErroDeEstoque):
    """O produto não pode ser removido porque possui histórico de movimentações."""
