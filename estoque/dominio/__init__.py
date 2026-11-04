"""Camada de domínio: entidades, movimentações, validações e erros."""

from .erros import (
    DadosInvalidos,
    ErroDeEstoque,
    EstoqueInsuficiente,
    MovimentacaoInconsistente,
    NomeDuplicado,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
    SaldoDesatualizado,
)
from .movimentacao import Ajuste, Entrada, Movimentacao, Saida
from .produto import Produto

__all__ = [
    "Ajuste",
    "DadosInvalidos",
    "Entrada",
    "ErroDeEstoque",
    "EstoqueInsuficiente",
    "Movimentacao",
    "MovimentacaoInconsistente",
    "NomeDuplicado",
    "Produto",
    "ProdutoComMovimentacoes",
    "ProdutoNaoEncontrado",
    "Saida",
    "SaldoDesatualizado",
]
