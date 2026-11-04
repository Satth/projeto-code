"""Camada de aplicação: casos de uso, modelos e contratos."""

from .modelos import MovimentacaoRegistrada, ProdutoComId
from .portas import RepositorioEstoquePorta
from .servico import ServicoEstoque

__all__ = [
    "MovimentacaoRegistrada",
    "ProdutoComId",
    "RepositorioEstoquePorta",
    "ServicoEstoque",
]
