"""Módulo da comanda adaptado ao domínio de Estoque.

As funções do domínio não possuem print.
Quem imprime é quem chama.

A regra de desconto considera somente os itens válidos
existentes no catálogo.
"""

from decimal import Decimal


PRECOS = {
    "teclado": Decimal("150.00"),
    "mouse": Decimal("80.00"),
    "monitor": Decimal("900.00"),
}


def itens_validos(comanda, precos=PRECOS):
    """Devolve apenas os itens que existem no catálogo."""
    validos = []

    for item in comanda:
        if item in precos:
            validos.append(item)

    return validos


def subtotal(comanda, precos=PRECOS):
    """Soma o preço dos itens válidos."""
    total = Decimal("0.00")

    for item in itens_validos(comanda, precos):
        total += precos[item]

    return total


def desconto(comanda, valor, minimo=3):
    """Aplica desconto de 10% a partir de três itens válidos."""
    if len(itens_validos(comanda)) >= minimo:
        return valor * Decimal("0.10")

    return Decimal("0.00")


def fechar(comanda):
    """Devolve subtotal, desconto e total da comanda."""
    sub = subtotal(comanda)
    desc = desconto(comanda, sub)

    return {
        "subtotal": sub,
        "desconto": desc,
        "total": sub - desc,
    }
