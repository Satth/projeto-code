# Exercício 01 - Dois objetos, dois estados
# Controle de Estoque - Composto por Eduardo Henrique, Matheus, Roberto Soares, Vinicius e Tiago

class Produto:
    def __init__(self, nome, quantidade):
        self.nome = nome
        self.quantidade = quantidade

    def adicionar_estoque(self, quantidade):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser positiva.")
        self.quantidade += quantidade


# Criação de duas instâncias com estados independentes
produto1 = Produto("Teclado", 10)
produto2 = Produto("Mouse", 20)

# Alterando apenas o primeiro produto
produto1.adicionar_estoque(5)

print(f"{produto1.nome}: {produto1.quantidade}")
print(f"{produto2.nome}: {produto2.quantidade}")
