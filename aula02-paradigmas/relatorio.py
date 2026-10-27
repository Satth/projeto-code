from functools import reduce


def acima_do_minimo(venda):
    """diz se a venda entra no relatorio."""
    return venda["valor"] > VALOR_MINIMO


def normalizar_categoria(categoria):
    """devolve a forma usada para comparar e exibir a categoria.

    A mesma funcao e usada pelo calculo do imposto e pelo agrupamento.
    Assim, "tela", "Tela" e " TELA " viram a mesma chave legivel "Tela",
    em vez de aparecerem separadas no relatorio.
    """
    if not isinstance(categoria, str) or not categoria.strip():
        raise ValueError("categoria deve ser um texto nao vazio")
    return categoria.strip().capitalize()


def aplicar_imposto(venda):
    """devolve uma nova venda com o imposto conforme a categoria.

    O enunciado atual do exercicio calcula uma deducao:
    valor * (1 - imposto). A formula foi preservada; a duvida sobre se o
    exercicio esperava deducao ou acrescimo esta registrada no README.
    """
    categoria = normalizar_categoria(venda["categoria"]).lower()

    if categoria == "periferico":
        imposto = 0.10
    elif categoria == "tela":
        imposto = 0.15
    else:
        imposto = 0.05

    return {**venda, "valor": venda["valor"] * (1 - imposto)}


def agrupar_por_categoria(acumulado, venda):
    """Soma a venda no total da sua categoria normalizada."""
    cat = normalizar_categoria(venda["categoria"])
    return {**acumulado, cat: acumulado.get(cat, 0) + venda["valor"]}


VENDAS = [
    {"produto": "teclado", "valor": 150.00, "categoria": "periferico"},
    {"produto": "mouse", "valor": 80.00, "categoria": "periferico"},
    {"produto": "monitor", "valor": 900.00, "categoria": "tela"},
    {"produto": "cabo HDMI", "valor": 35.00, "categoria": "acessorio"},
    {"produto": "headset", "valor": 250.00, "categoria": "periferico"},
    {"produto": "suporte", "valor": 120.00, "categoria": "acessorio"},
]

VALOR_MINIMO = 100.00


def relatorio(venda):
    """Total liquido por categoria, apenas de venda acima do minimo."""
    relevantes = filter(acima_do_minimo, venda)
    liquidas = map(aplicar_imposto, relevantes)
    return reduce(agrupar_por_categoria, liquidas, {})


if __name__ == "__main__":
    for categoria, total in relatorio(VENDAS).items():
        print(f"{categoria:12} R$ {total:8.2f}")
