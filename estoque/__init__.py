"""Domínio aplicado de controle de estoque.

O pacote está organizado em camadas:

- ``dominio``: entidades, movimentações, validações e exceções;
- ``aplicacao``: casos de uso, modelos de resultado e portas;
- ``infraestrutura.sqlite``: conexão, schema e repositório concretos;
- ``apresentacao``: interface de linha de comando.

A fachada pública expõe os contratos de domínio e de aplicação. Detalhes
concretos de SQLite permanecem em ``estoque.infraestrutura.sqlite``.
"""

from .aplicacao.modelos import MovimentacaoRegistrada, ProdutoComId
from .aplicacao.portas import RepositorioEstoquePorta
from .aplicacao.servico import ServicoEstoque
from .dominio.erros import (
    DadosInvalidos,
    ErroDeEstoque,
    EstoqueInsuficiente,
    MovimentacaoInconsistente,
    NomeDuplicado,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
    SaldoDesatualizado,
)
from .dominio.movimentacao import Ajuste, Entrada, Movimentacao, Saida
from .dominio.produto import Produto

__all__ = [
    "Ajuste",
    "DadosInvalidos",
    "Entrada",
    "ErroDeEstoque",
    "EstoqueInsuficiente",
    "Movimentacao",
    "MovimentacaoInconsistente",
    "MovimentacaoRegistrada",
    "NomeDuplicado",
    "Produto",
    "ProdutoComId",
    "ProdutoComMovimentacoes",
    "ProdutoNaoEncontrado",
    "RepositorioEstoquePorta",
    "Saida",
    "SaldoDesatualizado",
    "ServicoEstoque",
]
