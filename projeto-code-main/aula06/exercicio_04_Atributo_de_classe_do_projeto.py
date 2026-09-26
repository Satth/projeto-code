# Exercício 04 - Atributo de classe do projeto
# Controle de Estoque - Composto por Eduardo Henrique, Matheus, Roberto Soares, Vinicius e Tiago

class Produto:
    # Atributo de classe (compartilhado por todos os produtos)
    nome_do_sistema = "Sistema de Controle de Estoque"

    def __init__(self, nome, quantidade):
        self.nome = nome
        self.quantidade = quantidade


# Criação de duas instâncias (dois objetos)
produto1 = Produto("Teclado", 10)
produto2 = Produto("Mouse", 20)

# Provando que ambos compartilham o mesmo valor do atributo de classe
print(f"Produto 1 ({produto1.nome}): {produto1.nome_do_sistema}")
print(f"Produto 2 ({produto2.nome}): {produto2.nome_do_sistema}")

# Também podemos acessar direto pela classe
print(f"Acesso pela classe: {Produto.nome_do_sistema}")