"""Domínio aplicado de controle de estoque.

O pacote reúne a implementação integrada usada na demonstração:

- ``produto``: objeto de domínio e invariantes;
- ``movimentacao``: contrato e operações de entrada, saída e ajuste;
- ``banco``: conexão e schema SQLite;
- ``repositorio``: leitura e escrita no SQLite;
- ``servico``: regras de negócio que coordenam as operações.

Os exercícios independentes das pastas ``aula02`` a ``aula06`` continuam
existindo separadamente e não dependem deste pacote.
"""

from .banco import criar_conexao, criar_tabelas
from .erros import (
    DadosInvalidos,
    ErroDeEstoque,
    EstoqueInsuficiente,
    NomeDuplicado,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
)
from .movimentacao import Ajuste, Entrada, Movimentacao, Saida
from .produto import Produto
from .repositorio import (
    MovimentacaoRegistrada,
    ProdutoComId,
    RepositorioEstoque,
)
from .servico import ServicoEstoque

__all__ = [
    "Ajuste",
    "DadosInvalidos",
    "Entrada",
    "ErroDeEstoque",
    "EstoqueInsuficiente",
    "Movimentacao",
    "MovimentacaoRegistrada",
    "NomeDuplicado",
    "Produto",
    "ProdutoComId",
    "ProdutoComMovimentacoes",
    "ProdutoNaoEncontrado",
    "RepositorioEstoque",
    "Saida",
    "ServicoEstoque",
    "criar_conexao",
    "criar_tabelas",
]
