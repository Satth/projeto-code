"""Prática 3: estruturas condicionais.

Regra de frete:
  com cupom, ou acima de R$ 300  -> frete zero
  de R$ 100 até R$ 300           -> R$ 8
  abaixo de R$ 100               -> R$ 15

Rode com:  python pratica3_frete.py
"""

valor = float(input("Valor da compra: "))
cupom = input("Tem cupom? (s/n) ").lower() == "s"

if cupom or valor > 300:
    frete = 0.0
elif valor >= 100:
    frete = 8.0
else:
    frete = 15.0

print(f"Frete: R$ {frete:.2f}")
print(f"Total: R$ {valor + frete:.2f}")
