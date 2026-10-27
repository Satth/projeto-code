"""Prova de persistência real em arquivo SQLite após reconexão."""

from decimal import Decimal

from estoque.banco import criar_conexao, criar_tabelas
from estoque.repositorio import RepositorioEstoque
from estoque.servico import ServicoEstoque


def test_produtos_e_historico_sobrevivem_ao_fechar_e_reabrir(tmp_path):
    caminho = tmp_path / "estoque.db"

    conexao = criar_conexao(caminho)
    criar_tabelas(conexao)
    servico = ServicoEstoque(RepositorioEstoque(conexao))

    item = servico.cadastrar("Teclado", "150.00", 10, 5)
    servico.dar_entrada(item.id, 2, "compra")
    servico.dar_saida(item.id, 3, "venda")
    conexao.close()

    # Nova conexão para o mesmo arquivo: simula encerrar e abrir o programa.
    outra_conexao = criar_conexao(caminho)
    criar_tabelas(outra_conexao)
    outro_servico = ServicoEstoque(RepositorioEstoque(outra_conexao))

    recuperado = outro_servico.buscar(item.id)
    assert recuperado.nome == "Teclado"
    assert recuperado.quantidade == 9
    assert recuperado.produto.preco_unitario == Decimal("150.00")
    assert recuperado.produto.quantidade_minima == 5

    historico = outro_servico.historico(item.id)
    assert [registro.tipo for registro in historico] == ["entrada", "saida"]
    assert [registro.quantidade_anterior for registro in historico] == [10, 12]
    assert [registro.quantidade_nova for registro in historico] == [12, 9]
    assert [registro.observacao for registro in historico] == [
        "compra",
        "venda",
    ]

    outra_conexao.close()
