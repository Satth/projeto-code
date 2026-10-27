"""Demonstração interativa do controle de estoque com SQLite.

Execute na raiz do projeto:

    python -m estoque

O banco fica em ``estoque.db`` por padrão. Defina a variável de ambiente
``ESTOQUE_DB`` para usar outro caminho, por exemplo em uma demonstração
com um arquivo temporário.
"""

import os
from pathlib import Path

from .banco import criar_conexao, criar_tabelas
from .erros import DadosInvalidos, ErroDeEstoque
from .repositorio import RepositorioEstoque
from .servico import ServicoEstoque

MENU = """
1 - Listar produtos
2 - Cadastrar produto
3 - Registrar entrada
4 - Registrar saída
5 - Ajustar quantidade
6 - Ver histórico
7 - Produtos abaixo do mínimo
8 - Atualizar produto
9 - Remover produto
0 - Sair
"""


def _ler_inteiro(mensagem):
    try:
        return int(input(mensagem).strip())
    except ValueError as erro:
        raise DadosInvalidos("informe um número inteiro") from erro


def _exibir_produto(item):
    produto = item.produto
    situacao = "ABAIXO DO MÍNIMO" if produto.abaixo_do_minimo() else "OK"
    print(
        f"[{item.id}] {produto.nome} | "
        f"quantidade: {produto.quantidade} | "
        f"mínimo: {produto.quantidade_minima} | "
        f"preço: R$ {produto.preco_unitario:.2f} | {situacao}"
    )


def _listar(servico):
    itens = servico.listar()
    if not itens:
        print("Nenhum produto cadastrado.")
        return
    for item in itens:
        _exibir_produto(item)


def _cadastrar(servico):
    nome = input("Nome: ")
    preco = input("Preço unitário: ")
    quantidade = _ler_inteiro("Quantidade inicial: ")
    minimo = _ler_inteiro("Quantidade mínima: ")
    item = servico.cadastrar(nome, preco, quantidade, minimo)
    print("Produto cadastrado:")
    _exibir_produto(item)


def _movimentar(servico, operacao):
    produto_id = _ler_inteiro("ID do produto: ")
    quantidade = _ler_inteiro("Quantidade: ")
    observacao = input("Observação (opcional): ")
    item = operacao(produto_id, quantidade, observacao)
    print("Operação registrada:")
    _exibir_produto(item)


def _historico(servico):
    texto = input("ID do produto (vazio para todos): ").strip()
    produto_id = int(texto) if texto else None
    registros = servico.historico(produto_id)
    if not registros:
        print("Nenhuma movimentação registrada.")
        return
    for registro in registros:
        observacao = f" | {registro.observacao}" if registro.observacao else ""
        print(
            f"#{registro.id} {registro.criado_em} | {registro.produto_nome} | "
            f"{registro.tipo} | informado: {registro.quantidade} | "
            f"{registro.quantidade_anterior} -> {registro.quantidade_nova}"
            f"{observacao}"
        )


def _abaixo_do_minimo(servico):
    itens = servico.abaixo_do_minimo()
    if not itens:
        print("Nenhum produto abaixo do estoque mínimo.")
        return
    for item in itens:
        _exibir_produto(item)


def _atualizar(servico):
    produto_id = _ler_inteiro("ID do produto: ")
    nome = input("Novo nome: ")
    preco = input("Novo preço unitário: ")
    minimo = _ler_inteiro("Nova quantidade mínima: ")
    item = servico.atualizar(produto_id, nome, preco, minimo)
    print("Produto atualizado:")
    _exibir_produto(item)


def _remover(servico):
    produto_id = _ler_inteiro("ID do produto: ")
    confirmacao = input(
        f"Confirma a remoção do produto {produto_id}? (s/n) "
    ).strip().lower()
    if confirmacao != "s":
        print("Remoção cancelada.")
        return
    servico.remover(produto_id)
    print("Produto removido.")


def main():
    caminho = os.environ.get("ESTOQUE_DB", "estoque.db")
    conexao = criar_conexao(caminho)
    try:
        criar_tabelas(conexao)
        servico = ServicoEstoque(RepositorioEstoque(conexao))
        print(f"Banco: {Path(caminho).resolve()}")

        while True:
            print(MENU)
            opcao = input("Opção: ").strip()
            try:
                if opcao == "1":
                    _listar(servico)
                elif opcao == "2":
                    _cadastrar(servico)
                elif opcao == "3":
                    _movimentar(servico, servico.dar_entrada)
                elif opcao == "4":
                    _movimentar(servico, servico.dar_saida)
                elif opcao == "5":
                    _movimentar(servico, servico.ajustar)
                elif opcao == "6":
                    _historico(servico)
                elif opcao == "7":
                    _abaixo_do_minimo(servico)
                elif opcao == "8":
                    _atualizar(servico)
                elif opcao == "9":
                    _remover(servico)
                elif opcao == "0":
                    print("Até logo.")
                    break
                else:
                    print("Opção inválida.")
            except ErroDeEstoque as erro:
                print(f"Erro: {erro}")
            except ValueError as erro:
                print(f"Entrada inválida: {erro}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
