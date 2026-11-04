"""Implementação SQLite da persistência, compatível com a porta da aplicação."""

from .banco import SCHEMA, criar_conexao, criar_tabelas
from .repositorio import RepositorioEstoque

__all__ = [
    "RepositorioEstoque",
    "SCHEMA",
    "criar_conexao",
    "criar_tabelas",
]
