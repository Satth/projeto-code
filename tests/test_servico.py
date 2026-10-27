"""Testes das regras de negócio coordenadas pelo serviço."""

from decimal import Decimal

import pytest

from estoque.erros import (
    DadosInvalidos,
    EstoqueInsuficiente,
    NomeDuplicado,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
    SaldoDesatualizado,
)


def test_cadastrar_buscar_e_listar(servico):
    teclado = servico.cadastrar("Teclado", "150.00", 8, 5)
    mouse = servico.cadastrar("Mouse", "80.00", 3, 5)

    assert teclado.id == 1
    assert teclado.nome == "Teclado"
    assert teclado.quantidade == 8
    assert mouse.id == 2

    assert servico.buscar(1).nome == "Teclado"
    assert [item.nome for item in servico.listar()] == ["Teclado", "Mouse"]


@pytest.mark.parametrize(
    "argumentos",
    [
        ("", "10.00", 0, 0),
        ("Teclado", 0, 0, 0),
        ("Teclado", "10.00", -1, 0),
        ("Teclado", "10.00", 0, -1),
        ("Teclado", "10.00", 1.5, 0),
    ],
)
def test_cadastro_invalido_nao_persiste(servico, argumentos):
    with pytest.raises(DadosInvalidos):
        servico.cadastrar(*argumentos)

    assert servico.listar() == []


def test_nome_duplicado_e_recusado_sem_ignorar_caixa(servico):
    servico.cadastrar("Teclado", "150.00", 0, 0)

    with pytest.raises(NomeDuplicado):
        servico.cadastrar("teclado", "80.00", 0, 0)

    assert len(servico.listar()) == 1


def test_buscar_inexistente(servico):
    with pytest.raises(ProdutoNaoEncontrado):
        servico.buscar(99)


def test_atualizar_preserva_o_saldo_e_valida_o_nome(servico):
    item = servico.cadastrar("Teclado", "150.00", 8, 5)
    servico.dar_entrada(item.id, 2, "compra")

    atualizado = servico.atualizar(item.id, "Teclado ABNT", "160.50", 4)

    assert atualizado.nome == "Teclado ABNT"
    assert atualizado.produto.preco_unitario == Decimal("160.50")
    assert atualizado.produto.quantidade_minima == 4
    assert atualizado.quantidade == 10
    assert servico.buscar(item.id).quantidade == 10


def test_atualizar_com_nome_duplicado_nao_altera_o_banco(servico):
    servico.cadastrar("Teclado", "150.00", 0, 0)
    mouse = servico.cadastrar("Mouse", "80.00", 0, 0)

    with pytest.raises(NomeDuplicado):
        servico.atualizar(mouse.id, "teclado", "90.00", 0)

    assert servico.buscar(mouse.id).nome == "Mouse"


def test_atualizar_inexistente(servico):
    with pytest.raises(ProdutoNaoEncontrado):
        servico.atualizar(99, "Teclado", "150.00", 5)


def test_remover_produto_sem_historico(servico):
    item = servico.cadastrar("Teclado", "150.00", 0, 0)

    servico.remover(item.id)

    with pytest.raises(ProdutoNaoEncontrado):
        servico.buscar(item.id)


def test_remover_inexistente(servico):
    with pytest.raises(ProdutoNaoEncontrado):
        servico.remover(99)


def test_remover_produto_com_historico_preserva_os_dados(servico):
    item = servico.cadastrar("Teclado", "150.00", 10, 5)
    servico.dar_entrada(item.id, 2, "compra")

    with pytest.raises(ProdutoComMovimentacoes):
        servico.remover(item.id)

    assert servico.buscar(item.id).quantidade == 12
    assert len(servico.historico(item.id)) == 1


def test_entrada_e_saida_registram_historico(servico):
    item = servico.cadastrar("Teclado", "150.00", 10, 5)

    entrada = servico.dar_entrada(item.id, 5, "compra do fornecedor")
    assert entrada.quantidade == 15

    saida = servico.dar_saida(item.id, 3, "venda")
    assert saida.quantidade == 12

    historico = servico.historico(item.id)
    assert [registro.tipo for registro in historico] == ["entrada", "saida"]
    assert [registro.quantidade for registro in historico] == [5, 3]
    assert [registro.quantidade_anterior for registro in historico] == [10, 15]
    assert [registro.quantidade_nova for registro in historico] == [15, 12]
    assert [registro.observacao for registro in historico] == [
        "compra do fornecedor",
        "venda",
    ]
    assert servico.historico() == historico


def test_saida_acima_do_disponivel_falha_sem_alterar_dados(servico):
    item = servico.cadastrar("Teclado", "150.00", 2, 0)

    with pytest.raises(EstoqueInsuficiente):
        servico.dar_saida(item.id, 3)

    assert servico.buscar(item.id).quantidade == 2
    assert servico.historico(item.id) == []


def test_ajuste_registra_historico(servico):
    item = servico.cadastrar("Teclado", "150.00", 10, 5)

    ajustado = servico.ajustar(item.id, 4, "inventário")

    assert ajustado.quantidade == 4

    registro = servico.historico(item.id)[0]
    assert registro.tipo == "ajuste"
    assert registro.quantidade == 4
    assert registro.quantidade_anterior == 10
    assert registro.quantidade_nova == 4
    assert registro.observacao == "inventário"


def test_produtos_abaixo_do_minimo(servico):
    servico.cadastrar("No limite", "10.00", 5, 5)
    servico.cadastrar("Abaixo", "10.00", 4, 5)
    servico.cadastrar("Zerado", "10.00", 0, 1)

    itens = servico.abaixo_do_minimo()

    assert [item.nome for item in itens] == ["Abaixo", "Zerado"]


def test_movimentacao_em_produto_inexistente(servico):
    with pytest.raises(ProdutoNaoEncontrado):
        servico.dar_entrada(99, 1)

    with pytest.raises(ProdutoNaoEncontrado):
        servico.dar_saida(99, 1)

    with pytest.raises(ProdutoNaoEncontrado):
        servico.ajustar(99, 1)


def test_historico_de_produto_inexistente(servico):
    with pytest.raises(ProdutoNaoEncontrado):
        servico.historico(99)


def test_operacoes_invalidas_preservam_as_invariantes(servico):
    item = servico.cadastrar("Teclado", "150.00", 5, 2)

    with pytest.raises(DadosInvalidos):
        servico.dar_entrada(item.id, 0)

    with pytest.raises(DadosInvalidos):
        servico.dar_saida(item.id, -1)

    with pytest.raises(DadosInvalidos):
        servico.ajustar(item.id, -1)

    with pytest.raises(EstoqueInsuficiente):
        servico.dar_saida(item.id, 6)

    assert servico.buscar(item.id).quantidade == 5
    assert servico.historico(item.id) == []


def test_falha_na_persistencia_do_historico_nao_altera_o_banco(
    servico, repositorio, monkeypatch
):
    item = servico.cadastrar("Teclado", "150.00", 10, 5)

    def falhar_ao_registrar(**kwargs):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(
        repositorio, "_registrar_movimentacao", falhar_ao_registrar
    )

    with pytest.raises(RuntimeError):
        servico.dar_saida(item.id, 4)

    assert servico.buscar(item.id).quantidade == 10
    assert servico.historico(item.id) == []


def test_conflito_de_saldo_entre_leitura_e_gravacao(
    servico, repositorio, conexao, monkeypatch
):
    item = servico.cadastrar("Teclado", "150.00", 10, 5)
    aplicar_original = repositorio.aplicar_movimentacao

    def aplicar_com_saldo_alterado(**kwargs):
        conexao.execute(
            "UPDATE produtos SET quantidade = 20 WHERE id = ?", (item.id,)
        )
        conexao.commit()
        return aplicar_original(**kwargs)

    monkeypatch.setattr(
        repositorio, "aplicar_movimentacao", aplicar_com_saldo_alterado
    )

    with pytest.raises(SaldoDesatualizado):
        servico.dar_entrada(item.id, 5)

    assert servico.buscar(item.id).quantidade == 20
    assert servico.historico(item.id) == []
