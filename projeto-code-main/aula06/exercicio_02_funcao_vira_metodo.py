# Exercício 02 - Mais uma função vira método
# Controle de Estoque - Composto por Eduardo Henrique, Matheus, Roberto Soares, Vinicius e Tiago

class Produto:
    def __init__(self, nome, quantidade, estoque_minimo):
        self.nome = nome
        self.quantidade = quantidade
        self.estoque_minimo = estoque_minimo

    # Função do domínio transformada em método
    def verificar_estoque_minimo(self):
        return self.quantidade < self.estoque_minimo


# Exemplo de utilização
produto = Produto("Teclado", 5, 10)

print(f"Produto: {produto.nome}")
print(f"Quantidade: {produto.quantidade}")
print(f"Estoque mínimo: {produto.estoque_minimo}")
print(f"Abaixo do estoque mínimo? {produto.verificar_estoque_minimo()}")


# Antes, a função poderia ser chamada assim:
# verificar_estoque_minimo(quantidade, estoque_minimo)

# Depois de virar método:
# produto.verificar_estoque_minimo()
