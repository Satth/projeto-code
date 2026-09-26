"""Prática 4: dicionário com lista dentro, laço e condicional.

Rode com:  python pratica4_diario.py
"""

turma = {"Ana": [8.0, 9.5], "Bruno": [6.0, 5.5], "Carla": [4.0, 3.5]}

medias = []

for nome, notas in turma.items():
    media = sum(notas) / len(notas)
    medias.append(media)

    if media >= 7:
        situacao = "Aprovado"
    elif media >= 5:
        situacao = "Recuperação"
    else:
        situacao = "Reprovado"

    print(f"{nome:<8} {media:.1f}  {situacao}")

print(f"Média da turma: {sum(medias) / len(medias):.2f}")
