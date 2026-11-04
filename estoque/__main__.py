"""Ponto de composição da aplicação de controle de estoque.

Execute na raiz do projeto:

    python -m estoque

O banco fica em ``estoque.db`` por padrão. Defina a variável de ambiente
``ESTOQUE_DB`` para usar outro caminho, por exemplo em uma demonstração
com um arquivo temporário.

Este módulo apenas monta as dependências concretas: caminho, conexão,
tabelas, repositório SQLite, serviço e CLI. As regras ficam no domínio e
na aplicação.
"""

import os

from .aplicacao.servico import ServicoEstoque
from .apresentacao.cli import executar
from .infraestrutura.sqlite.banco import criar_conexao, criar_tabelas
from .infraestrutura.sqlite.repositorio import RepositorioEstoque


def main():
    caminho = os.environ.get("ESTOQUE_DB", "estoque.db")
    conexao = criar_conexao(caminho)
    try:
        criar_tabelas(conexao)
        servico = ServicoEstoque(RepositorioEstoque(conexao))
        executar(servico, caminho)
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
