"""Suíte de testes da comanda do domínio de Estoque.

Rode com: python -m pytest -q
"""

from decimal import Decimal

from comanda import fechar, itens_validos, subtotal


def test_subtotal_soma_apenas_o_que_esta_no_catalogo():
    assert subtotal(["teclado", "mouse", "webcam"]) == Decimal("230.00")


def test_item_fora_do_catalogo_nao_conta_para_o_desconto():
    conta = fechar(["teclado", "mouse", "webcam"])
    assert conta["desconto"] == Decimal("0.00")


def test_desconto_de_dez_por_cento_a_partir_de_tres_itens():
    conta = fechar(["teclado", "mouse", "monitor"])

    assert conta["subtotal"] == Decimal("1130.00")
    assert conta["desconto"] == Decimal("113.00")
    assert conta["total"] == Decimal("1017.00")


def test_comanda_vazia_nao_quebra():
    assert fechar([])["total"] == Decimal("0.00")


def test_itens_validos_ignora_desconhecido():
    assert itens_validos(["teclado", "webcam"]) == ["teclado"]
