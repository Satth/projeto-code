"""Contrato das movimentações de estoque e suas implementações.

``Movimentacao`` define o contrato ``aplicar(produto)``. O serviço chama
esse método sem saber se a operação concreta é uma entrada, uma saída ou
um ajuste: é o polimorfismo sendo usado para simplificar a regra.
"""

from abc import ABC, abstractmethod

from .produto import Produto
from .validacao import (
    validar_inteiro,
    validar_observacao,
    validar_quantidade_positiva,
)


class Movimentacao(ABC):
    """Contrato de uma operação que altera o saldo de um produto."""

    tipo = ""

    def __init__(self, quantidade, observacao=""):
        self.quantidade = validar_quantidade_positiva(quantidade)
        self.observacao = validar_observacao(observacao)

    @abstractmethod
    def aplicar(self, produto: Produto) -> None:
        """Aplica a operação ao produto, preservando as invariantes."""
        raise NotImplementedError


class Entrada(Movimentacao):
    """Acrescenta unidades ao saldo."""

    tipo = "entrada"

    def aplicar(self, produto):
        produto.repor(self.quantidade)


class Saida(Movimentacao):
    """Retira unidades do saldo, respeitando a disponibilidade."""

    tipo = "saida"

    def aplicar(self, produto):
        produto.retirar(self.quantidade)


class Ajuste(Movimentacao):
    """Define o saldo para uma nova quantidade absoluta.

    Aqui ``quantidade`` significa o novo saldo desejado, e não um delta.
    O histórico registra também o saldo anterior e o novo saldo, deixando
    a operação compreensível.
    """

    tipo = "ajuste"

    def __init__(self, nova_quantidade, observacao=""):
        self.quantidade = validar_inteiro(nova_quantidade, "nova quantidade")
        self.observacao = validar_observacao(observacao)

    def aplicar(self, produto):
        produto.ajustar(self.quantidade)
