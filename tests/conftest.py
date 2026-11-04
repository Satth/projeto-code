"""Fixtures compartilhadas pelos testes da implementação integrada.

Cada teste recebe uma conexão SQLite em um arquivo temporário diferente,
garantindo isolamento e evitando contaminar o banco local ``estoque.db``.
"""

import pytest

from estoque.aplicacao.servico import ServicoEstoque
from estoque.infraestrutura.sqlite.banco import criar_conexao, criar_tabelas
from estoque.infraestrutura.sqlite.repositorio import RepositorioEstoque


@pytest.fixture
def conexao(tmp_path):
    conexao = criar_conexao(tmp_path / "estoque-teste.db")
    criar_tabelas(conexao)
    yield conexao
    conexao.close()


@pytest.fixture
def repositorio(conexao):
    return RepositorioEstoque(conexao)


@pytest.fixture
def servico(repositorio):
    return ServicoEstoque(repositorio)
