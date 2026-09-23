"""Prática 2: leitura do teclado, conversão de tipo e o erro do ponto flutuante.

Rode com:  python pratica2_orcamento.py
Teste com: preço 19.90 e quantidade 3
"""

preco = float(input("Preço unitário: "))
qtd = int(input("Quantidade: "))

total = preco * qtd
com_desconto = total * 0.9

# o número cru, com o erro de representação à mostra
print(total)

# o mesmo número formatado: a f-string esconde, não corrige
print(f"Total: R$ {com_desconto:.2f}")
