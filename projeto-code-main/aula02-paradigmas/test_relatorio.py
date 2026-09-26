from relatorio import relatorio


def test_caso_comum():
    vendas = [
        {"produto": "A", "valor": 200.00, "categoria": "X"},
        {"produto": "B", "valor": 300.00, "categoria": "X"},
    ]
    assert relatorio(vendas) == {"X": 475.00}


def test_lista_vazia():
    assert relatorio([]) == {}


def test_nenhuma_venda_passa_minimo():
    vendas = [
        {"produto": "A", "valor": 50.00, "categoria": "X"},
        {"produto": "B", "valor": 100.00, "categoria": "X"},
    ]
    assert relatorio(vendas) == {}


def test_agrupa_por_categoria():
    vendas = [
        {"produto": "A", "valor": 200.00, "categoria": "X"},
        {"produto": "A", "valor": 200.00, "categoria": "Y"},
    ]
    assert relatorio(vendas) == {"X": 190.00, "Y": 190.00}


def test_imposto_varia_por_categoria():
    vendas = [
        {"produto": "A", "valor": 200.00, "categoria": "Tela"},
    ]
    # 15% de imposto sobre 200 deixa 170
    assert relatorio(vendas) == {"Tela": 170.00}
