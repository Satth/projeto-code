"""Prática 5: controle de estoque do domínio da equipe.

Junta dicionário, lista, laço, condicional e Decimal.
O catálogo representa produtos e suas quantidades em estoque.

Rode com:  python pratica5_comanda.py
"""

from decimal import Decimal

estoque = {
    "teclado": {"quantidade": 8, "minimo": 5, "preco": Decimal("150.00")},
    "mouse": {"quantidade": 3, "minimo": 5, "preco": Decimal("80.00")},
    "monitor": {"quantidade": 10, "minimo": 3, "preco": Decimal("900.00")},
}

operacoes = [
    ("entrada", "teclado", 2),
    ("saida", "mouse", 1),
    ("ajuste", "monitor", 8),
    ("saida", "webcam", 1),
]

for tipo, produto, quantidade in operacoes:
    if produto not in estoque:
        print(f"produto fora do estoque: {produto}")
        continue

    if tipo == "entrada":
        estoque[produto]["quantidade"] += quantidade
    elif tipo == "saida":
        estoque[produto]["quantidade"] -= quantidade
    elif tipo == "ajuste":
        estoque[produto]["quantidade"] = quantidade

print("Estoque atual:")

for produto, dados in estoque.items():
    quantidade = dados["quantidade"]
    minimo = dados["minimo"]
    valor = quantidade * dados["preco"]

    if quantidade < minimo:
        situacao = "ALERTA: abaixo do estoque minimo"
    else:
        situacao = "OK"

    print(
        f"{produto:<10} "
        f"Quantidade: {quantidade:<3} "
        f"Valor: R$ {valor:>8.2f}  "
        f"{situacao}"
    )

# ATENÇÃO, defeito proposital:
# a operação de saída não verifica se a quantidade disponível
# é suficiente antes de diminuir o estoque.
# Este tipo de regra será aprofundado nas próximas etapas.
