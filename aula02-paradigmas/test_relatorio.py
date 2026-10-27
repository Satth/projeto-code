import pytest

from relatorio import normalizar_categoria, relatorio


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


def test_categorias_com_mesma_escrita_somam_juntas():
    vendas = [
        {"produto": "A", "valor": 200.00, "categoria": "Tela"},
        {"produto": "B", "valor": 200.00, "categoria": "Tela"},
    ]
    assert relatorio(vendas) == {"Tela": 340.00}


def test_categorias_com_capitalizacao_diferente_somam_juntas():
    vendas = [
        {"produto": "A", "valor": 200.00, "categoria": "Tela"},
        {"produto": "B", "valor": 200.00, "categoria": "tela"},
        {"produto": "C", "valor": 200.00, "categoria": "TELA"},
    ]
    # As tres vendas usam a mesma taxa e a mesma chave "Tela".
    assert relatorio(vendas) == {"Tela": pytest.approx(510.00)}


def test_categoria_com_espacos_normaliza_chave():
    vendas = [
        {"produto": "A", "valor": 200.00, "categoria": "  tela  "},
    ]
    assert relatorio(vendas) == {"Tela": 170.00}


def test_relatorio_com_multiplas_categorias_e_capitalizacao_mista():
    vendas = [
        {"produto": "A", "valor": 150.00, "categoria": "periferico"},
        {"produto": "B", "valor": 200.00, "categoria": "PERIFERICO"},
        {"produto": "C", "valor": 200.00, "categoria": "tela"},
        {"produto": "D", "valor": 120.00, "categoria": "Acessorio"},
    ]
    resultado = relatorio(vendas)

    assert resultado == {
        "Periferico": pytest.approx(315.00),
        "Tela": pytest.approx(170.00),
        "Acessorio": pytest.approx(114.00),
    }


def test_apenas_vendas_acima_do_limite_entram_no_relatorio():
    vendas = [
        {"produto": "A", "valor": 99.99, "categoria": "Tela"},
        {"produto": "B", "valor": 100.00, "categoria": "Tela"},
        {"produto": "C", "valor": 101.00, "categoria": "Acessorio"},
    ]
    assert relatorio(vendas) == {"Acessorio": pytest.approx(95.95)}


def test_categoria_invalida_e_recusada():
    assert normalizar_categoria("  tela  ") == "Tela"
    with pytest.raises(ValueError):
        normalizar_categoria("   ")
    with pytest.raises(ValueError):
        normalizar_categoria(None)
