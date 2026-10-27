"""Testes do contrato de movimentação e do polimorfismo entre operações."""

import pytest

from estoque.erros import DadosInvalidos, EstoqueInsuficiente
from estoque.movimentacao import Ajuste, Entrada, Movimentacao, Saida
from estoque.produto import Produto


def test_entrada_aumenta_o_saldo():
    produto = Produto("Teclado", "150.00", 10, 2)

    Entrada(5).aplicar(produto)

    assert produto.quantidade == 15


def test_saida_diminui_o_saldo():
    produto = Produto("Teclado", "150.00", 10, 2)

    Saida(4).aplicar(produto)

    assert produto.quantidade == 6


def test_saida_acima_do_disponivel_falha_e_preserva_o_saldo():
    produto = Produto("Teclado", "150.00", 3, 1)

    with pytest.raises(EstoqueInsuficiente):
        Saida(4).aplicar(produto)

    assert produto.quantidade == 3


def test_ajuste_define_o_saldo_absoluto():
    produto = Produto("Teclado", "150.00", 10, 2)

    Ajuste(4).aplicar(produto)
    assert produto.quantidade == 4

    Ajuste(0).aplicar(produto)
    assert produto.quantidade == 0


@pytest.mark.parametrize("classe", [Entrada, Saida])
@pytest.mark.parametrize("quantidade", [0, -1, 1.5, "2", True])
def test_entrada_e_saida_exigem_quantidade_positiva(classe, quantidade):
    with pytest.raises(DadosInvalidos):
        classe(quantidade)


@pytest.mark.parametrize("quantidade", [-1, 1.5, "2", True])
def test_ajuste_exige_quantidade_inteira_nao_negativa(quantidade):
    with pytest.raises(DadosInvalidos):
        Ajuste(quantidade)


def test_operacoes_seguem_o_mesmo_contrato():
    produto = Produto("Teclado", "150.00", 10, 2)
    operacoes = [Entrada(5), Saida(3), Ajuste(20)]

    for operacao in operacoes:
        assert isinstance(operacao, Movimentacao)
        operacao.aplicar(produto)

    assert produto.quantidade == 20
    assert [operacao.tipo for operacao in operacoes] == [
        "entrada",
        "saida",
        "ajuste",
    ]


def test_observacao_e_normalizada():
    entrada = Entrada(1, "  compra do fornecedor  ")

    assert entrada.observacao == "compra do fornecedor"
    assert Entrada(1).observacao == ""
