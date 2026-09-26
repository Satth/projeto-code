# Exercício 03 - Quebrem de propósito
# Controle de Estoque - Composto por Eduardo Henrique, Matheus, Roberto Soares, Vinicius e Tiago

class Produto:
    def __init__(self, nome, quantidade):
        self.nome = nome
        self._quantidade = quantidade

    @property
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, valor):
        if valor < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")

        self._quantidade = valor


# Criação de um produto
produto = Produto("Teclado", 10)

# Tentativa proposital de atribuir um valor inválido
try:
    produto.quantidade = -5
except ValueError as erro:
    print(f"Erro: {erro}")
