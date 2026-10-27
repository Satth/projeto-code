# Exercício 05 - Teste da invariante
# Controle de Estoque - Composto por Eduardo Henrique, Matheus, Roberto Soares, Vinicius e Tiago

import pytest

class Produto:
    def __init__(self, nome, quantidade):
        self.nome = nome
        self.quantidade = quantidade  # Aciona o setter abaixo

    @property
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, valor):
        if valor < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        self._quantidade = valor


# Teste usando o pytest para garantir que a regra (invariante) funciona
def test_quantidade_invalida_gera_erro():
    produto = Produto("Teclado", 10)

    # O pytest garante que o erro ValueError é lançado ao atribuir valor negativo
    with pytest.raises(ValueError):
        produto.quantidade = -5