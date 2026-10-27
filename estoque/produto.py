"""Objetos de domínio do controle de estoque."""

from .erros import EstoqueInsuficiente
from .validacao import (
    converter_preco,
    validar_inteiro,
    validar_quantidade_positiva,
    validar_texto,
)


class Produto:
    """Um produto e o seu saldo atual em estoque.

    A quantidade é exposta somente para leitura. Ela só muda pelos métodos
    de domínio ``repor``, ``retirar`` e ``ajustar``, que preservam a
    invariante de que o saldo nunca fica negativo. Preço e nome também
    possuem setters porque são alterados na atualização cadastral, mas
    sempre passam pela validação correspondente.
    """

    def __init__(self, nome, preco_unitario, quantidade=0, quantidade_minima=0):
        self.nome = nome
        self.preco_unitario = preco_unitario
        self.quantidade_minima = quantidade_minima
        self._quantidade = validar_inteiro(quantidade, "quantidade")

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        self._nome = validar_texto(valor, "nome")

    @property
    def preco_unitario(self):
        return self._preco_unitario

    @preco_unitario.setter
    def preco_unitario(self, valor):
        self._preco_unitario = converter_preco(valor)

    @property
    def quantidade(self):
        return self._quantidade

    @property
    def quantidade_minima(self):
        return self._quantidade_minima

    @quantidade_minima.setter
    def quantidade_minima(self, valor):
        self._quantidade_minima = validar_inteiro(valor, "quantidade mínima")

    @property
    def valor_total(self):
        """Valor monetário do saldo atual (preço unitário × quantidade)."""
        return self.preco_unitario * self.quantidade

    def abaixo_do_minimo(self):
        """Indica se o saldo atual está abaixo do estoque mínimo."""
        return self.quantidade < self.quantidade_minima

    def repor(self, quantidade):
        """Soma uma entrada positiva ao saldo."""
        self._quantidade += validar_quantidade_positiva(
            quantidade, "quantidade de entrada"
        )

    def retirar(self, quantidade):
        """Retira uma quantidade positiva, recusando saldo insuficiente."""
        quantidade = validar_quantidade_positiva(quantidade, "quantidade de saída")
        if quantidade > self._quantidade:
            raise EstoqueInsuficiente(
                f"estoque insuficiente para {self.nome}: "
                f"disponível {self._quantidade}, solicitado {quantidade}"
            )
        self._quantidade -= quantidade

    def ajustar(self, nova_quantidade):
        """Define o saldo para um novo valor absoluto (ajuste de inventário)."""
        self._quantidade = validar_inteiro(nova_quantidade, "nova quantidade")

    def __repr__(self):
        return (
            f"Produto(nome={self.nome!r}, "
            f"preco_unitario={self.preco_unitario!r}, "
            f"quantidade={self.quantidade!r}, "
            f"quantidade_minima={self.quantidade_minima!r})"
        )
