"""Prática 1: variáveis, atribuição múltipla e troca de valores.

Rode com:  python pratica1_variaveis.py
"""

# 0. três variáveis de tipos diferentes em uma única linha
curso, semestre, turno = "ADS", 2, "noite"
print(curso, semestre, turno)

# 1. troca de valores sem variável auxiliar
curso, turno = turno, curso
print(curso, semestre, turno)

# 2. o mesmo valor para vários nomes
a = b = c = 0
print(a, b, c)

# 3. o tipo pertence ao valor, não ao nome
x = 5
print(type(x))
x = "cinco"
print(type(x))
