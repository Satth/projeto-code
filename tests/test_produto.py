"""Testes do objeto de domínio ``Produto`` e das suas invariantes."""

from decimal import Decimal

import pytest

from estoque.erros import DadosInvalidos, EstoqueInsuficiente
from estoque.produto import Produto


def test_produto_valido_mantem_estado_e_valor_total():
    produto = Produto("Teclado", "150.00", 8, 5)

    assert produto.nome == "Teclado"
    assert produto.preco_unitario == Decimal("150.00")
    assert produto.quantidade == 8
    assert produto.quantidade_minima == 5
    assert produto.valor_total == Decimal("1200.00")
    assert produto.abaixo_do_minimo() is False


@pytest.mark.parametrize("nome", ["", "   ", None, 123])
def test_nome_invalido_e_recusado(nome):
    with pytest.raises(DadosInvalidos):
        Produto(nome, "10.00", 0, 0)


@pytest.mark.parametrize(
    "preco",
    [0, "-10.00", "abc", None, True, float("nan"), "10.999"],
)
def test_preco_invalido_e_recusado(preco):
    with pytest.raises(DadosInvalidos):
        Produto("Teclado", preco, 0, 0)


@pytest.mark.parametrize("quantidade", [-1, 1.5, "2", True])
def test_quantidade_invalida_e_recusada(quantidade):
    with pytest.raises(DadosInvalidos):
        Produto("Teclado", "10.00", quantidade, 0)


@pytest.mark.parametrize("minimo", [-1, 1.5, "2", True])
def test_quantidade_minima_invalida_e_recusada(minimo):
    with pytest.raises(DadosInvalidos):
        Produto("Teclado", "10.00", 0, minimo)


def test_preco_aceita_inteiro_e_float_sem_erro_de_representacao():
    inteiro = Produto("Cabo", 10, 0)
    float_ = Produto("Adaptador", 19.9, 0)

    assert inteiro.preco_unitario == Decimal("10.00")
    assert float_.preco_unitario == Decimal("19.90")


def test_repor_e_retirar_atualizam_o_saldo():
    produto = Produto("Mouse", "80.00", 10, 3)

    produto.repor(5)
    assert produto.quantidade == 15

    produto.retirar(4)
    assert produto.quantidade == 11

    produto.retirar(11)
    assert produto.quantidade == 0


def test_retirada_acima_do_saldo_falha_e_preserva_o_estado():
    produto = Produto("Mouse", "80.00", 3, 1)

    with pytest.raises(EstoqueInsuficiente):
        produto.retirar(4)

    assert produto.quantidade == 3


@pytest.mark.parametrize("quantidade", [0, -1, 1.5, "2", True])
def test_repor_recusa_quantidade_invalida(quantidade):
    produto = Produto("Mouse", "80.00", 3, 1)

    with pytest.raises(DadosInvalidos):
        produto.repor(quantidade)

    assert produto.quantidade == 3


@pytest.mark.parametrize("quantidade", [0, -1, 1.5, "2", True])
def test_retirar_recusa_quantidade_invalida(quantidade):
    produto = Produto("Mouse", "80.00", 3, 1)

    with pytest.raises(DadosInvalidos):
        produto.retirar(quantidade)

    assert produto.quantidade == 3


def test_ajuste_controlado_aceita_zero_e_recusa_negativo():
    produto = Produto("Monitor", "900.00", 10, 2)

    produto.ajustar(4)
    assert produto.quantidade == 4

    produto.ajustar(0)
    assert produto.quantidade == 0

    with pytest.raises(DadosInvalidos):
        produto.ajustar(-1)

    assert produto.quantidade == 0


def test_estoque_minimo_no_limite_nao_esta_abaixo():
    produto = Produto("Teclado", "150.00", 5, 5)

    assert produto.abaixo_do_minimo() is False

    produto.retirar(1)
    assert produto.abaixo_do_minimo() is True


def test_atualizar_nome_e_preco_respeita_validacoes():
    produto = Produto("Teclado", "150.00", 8, 5)

    produto.nome = "  Teclado ABNT  "
    produto.preco_unitario = "160.50"
    produto.quantidade_minima = 4

    assert produto.nome == "Teclado ABNT"
    assert produto.preco_unitario == Decimal("160.50")
    assert produto.quantidade_minima == 4

    with pytest.raises(DadosInvalidos):
        produto.nome = "   "
    with pytest.raises(DadosInvalidos):
        produto.preco_unitario = 0
    with pytest.raises(DadosInvalidos):
        produto.quantidade_minima = -1
