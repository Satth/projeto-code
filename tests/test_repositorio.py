"""Testes da tradução entre domínio e SQLite."""

from decimal import Decimal

import pytest

from estoque.erros import (
    NomeDuplicado,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
)
from estoque.produto import Produto


def test_salvar_buscar_e_listar(repositorio):
    teclado_id = repositorio.salvar(Produto("Teclado", "150.00", 8, 5))
    mouse_id = repositorio.salvar(Produto("Mouse", "80.00", 3, 5))

    assert (teclado_id, mouse_id) == (1, 2)

    teclado = repositorio.buscar(teclado_id)
    assert teclado.nome == "Teclado"
    assert teclado.preco_unitario == Decimal("150.00")
    assert teclado.quantidade == 8
    assert teclado.quantidade_minima == 5

    itens = repositorio.listar()
    assert [item.id for item in itens] == [1, 2]
    assert [item.nome for item in itens] == ["Teclado", "Mouse"]
    assert [item.quantidade for item in itens] == [8, 3]


def test_buscar_inexistente_devolve_none(repositorio):
    assert repositorio.buscar(99) is None


def test_existe_nome_ignora_caixa_e_respeita_exceto_id(repositorio):
    produto_id = repositorio.salvar(Produto("Teclado", "150.00", 0, 0))

    assert repositorio.existe_nome("Teclado") is True
    assert repositorio.existe_nome("teclado") is True
    assert repositorio.existe_nome("TECLADO") is True
    assert repositorio.existe_nome("Mouse") is False
    assert repositorio.existe_nome("teclado", exceto_id=produto_id) is False
    assert repositorio.existe_nome("teclado", exceto_id=99) is True


def test_salvar_nome_duplicado_e_recusado(repositorio):
    repositorio.salvar(Produto("Teclado", "150.00", 0, 0))

    with pytest.raises(NomeDuplicado):
        repositorio.salvar(Produto("teclado", "80.00", 0, 0))


def test_atualizar_preserva_a_quantidade_e_recusa_id_inexistente(repositorio):
    produto_id = repositorio.salvar(Produto("Teclado", "100.00", 7, 2))
    produto = repositorio.buscar(produto_id)

    produto.nome = "Teclado novo"
    produto.preco_unitario = "120.00"
    produto.quantidade_minima = 4

    assert repositorio.atualizar(produto_id, produto) is True

    atualizado = repositorio.buscar(produto_id)
    assert atualizado.nome == "Teclado novo"
    assert atualizado.preco_unitario == Decimal("120.00")
    assert atualizado.quantidade_minima == 4
    assert atualizado.quantidade == 7

    assert repositorio.atualizar(99, produto) is False


def test_atualizar_para_nome_duplicado_e_recusado(repositorio):
    repositorio.salvar(Produto("Teclado", "150.00", 0, 0))
    mouse_id = repositorio.salvar(Produto("Mouse", "80.00", 0, 0))
    mouse = repositorio.buscar(mouse_id)
    mouse.nome = "teclado"

    with pytest.raises(NomeDuplicado):
        repositorio.atualizar(mouse_id, mouse)

    assert repositorio.buscar(mouse_id).nome == "Mouse"


def test_remover_produto_sem_movimentacoes(repositorio):
    produto_id = repositorio.salvar(Produto("Teclado", "150.00", 0, 0))

    assert repositorio.remover(produto_id) is True
    assert repositorio.buscar(produto_id) is None
    assert repositorio.remover(produto_id) is False


def test_aplicar_movimentacao_atualiza_saldo_e_grava_historico(repositorio):
    produto_id = repositorio.salvar(Produto("Teclado", "150.00", 10, 5))

    repositorio.aplicar_movimentacao(
        produto_id=produto_id,
        quantidade_anterior=10,
        nova_quantidade=6,
        tipo="saida",
        quantidade=4,
        observacao="venda ao cliente",
    )

    assert repositorio.buscar(produto_id).quantidade == 6

    historico = repositorio.listar_movimentacoes()
    assert len(historico) == 1

    registro = historico[0]
    assert registro.produto_id == produto_id
    assert registro.produto_nome == "Teclado"
    assert registro.tipo == "saida"
    assert registro.quantidade == 4
    assert registro.quantidade_anterior == 10
    assert registro.quantidade_nova == 6
    assert registro.observacao == "venda ao cliente"
    assert registro.criado_em

    assert repositorio.listar_movimentacoes(produto_id) == historico
    assert repositorio.listar_movimentacoes(99) == []


def test_movimentacao_em_produto_inexistente_nao_grava_historico(repositorio):
    with pytest.raises(ProdutoNaoEncontrado):
        repositorio.aplicar_movimentacao(
            produto_id=99,
            quantidade_anterior=0,
            nova_quantidade=1,
            tipo="entrada",
            quantidade=1,
            observacao="",
        )

    assert repositorio.listar_movimentacoes() == []


def test_remover_produto_com_historico_e_recusado(repositorio):
    produto_id = repositorio.salvar(Produto("Teclado", "150.00", 10, 5))
    repositorio.aplicar_movimentacao(
        produto_id=produto_id,
        quantidade_anterior=10,
        nova_quantidade=12,
        tipo="entrada",
        quantidade=2,
        observacao="compra",
    )

    with pytest.raises(ProdutoComMovimentacoes):
        repositorio.remover(produto_id)

    assert repositorio.buscar(produto_id) is not None
    assert len(repositorio.listar_movimentacoes(produto_id)) == 1


def test_falha_ao_gravar_historico_reverte_a_quantidade(repositorio, monkeypatch):
    produto_id = repositorio.salvar(Produto("Teclado", "150.00", 10, 5))

    def falhar_ao_registrar(**kwargs):
        raise RuntimeError("falha simulada ao gravar o histórico")

    # Injeção de falha real no segundo INSERT da mesma transação.
    monkeypatch.setattr(
        repositorio, "_registrar_movimentacao", falhar_ao_registrar
    )

    with pytest.raises(RuntimeError):
        repositorio.aplicar_movimentacao(
            produto_id=produto_id,
            quantidade_anterior=10,
            nova_quantidade=6,
            tipo="saida",
            quantidade=4,
            observacao="venda",
        )

    assert repositorio.buscar(produto_id).quantidade == 10
    assert repositorio.listar_movimentacoes() == []
