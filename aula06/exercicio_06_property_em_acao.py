# Exercício 06 - Property em ação
# Controle de Estoque - Composto por Eduardo Henrique, Matheus, Roberto Soares, Vinicius e Tiago

class Produto:
    def __init__(self, nome, quantidade, preco_unitario):
        self.nome = nome
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario

    # Método comum (precisa de parênteses para chamar)
    def calcular_desconto(self, porcentagem):
        return (self.quantidade * self.preco_unitario) * (porcentagem / 100)

    # Cálculo do domínio transformado em @property (não usa parênteses)
    @property
    def valor_total(self):
        return self.quantidade * self.preco_unitario


# Criando um produto
produto = Produto("Teclado", 10, 50.0)

# 1. Chamando o método comum: OBRIGATÓRIO usar parênteses ()
desconto = produto.calcular_desconto(10)
print(f"Desconto: R$ {desconto}")

# 2. Chamando a @property: NÃO USA parênteses ()
total = produto.valor_total
print(f"Valor total em estoque: R$ {total}")


# --- DIFERENÇA DE CHAMAR COM E SEM PARÊNTESES ---

# Se chamar a @property COM parênteses:
# produto.valor_total()
# Ocorre um erro (TypeError), pois o Python tenta executar o número final como se fosse uma função.

# Se chamar o método comum SEM parênteses:
# produto.calcular_desconto
# O Python apenas mostra a referência da função na memória, sem executar o cálculo.