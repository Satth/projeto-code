"""Testes das fronteiras arquiteturais entre as camadas do pacote."""

import ast
from pathlib import Path

RAIZ_ESTOQUE = Path(__file__).resolve().parents[1] / "estoque"


def _arquivos(pacote):
    return sorted((RAIZ_ESTOQUE / pacote).rglob("*.py"))


def _imports_do_arquivo(caminho):
    """Resolve imports relativos para nomes absolutos dentro do pacote."""
    partes = caminho.relative_to(RAIZ_ESTOQUE).with_suffix("").parts
    pacote_do_arquivo = ".".join(("estoque",) + partes[:-1])
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    modulos = set()

    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom):
            if no.level:
                base = pacote_do_arquivo.split(".")
                base = base[: len(base) - no.level + 1]
                prefixo = ".".join(base)
                modulo = f"{prefixo}.{no.module}" if no.module else prefixo
            else:
                modulo = no.module or ""
            if modulo:
                modulos.add(modulo)
    return modulos


def _pertence(modulo, prefixos):
    return any(
        modulo == prefixo or modulo.startswith(f"{prefixo}.")
        for prefixo in prefixos
    )


def test_dominio_nao_depende_de_aplicacao_infraestrutura_ou_apresentacao():
    proibidos = (
        "estoque.aplicacao",
        "estoque.infraestrutura",
        "estoque.apresentacao",
        "sqlite3",
    )

    for arquivo in _arquivos("dominio"):
        for modulo in _imports_do_arquivo(arquivo):
            assert not _pertence(modulo, proibidos), (
                f"{arquivo.name} importa {modulo}, violando a fronteira do domínio"
            )


def test_aplicacao_nao_depende_de_infraestrutura_ou_apresentacao():
    proibidos = ("estoque.infraestrutura", "estoque.apresentacao", "sqlite3")

    for arquivo in _arquivos("aplicacao"):
        for modulo in _imports_do_arquivo(arquivo):
            assert not _pertence(modulo, proibidos), (
                f"{arquivo.name} importa {modulo}, violando a fronteira da aplicação"
            )


def test_servico_nao_importa_repositorio_sqlite():
    imports = _imports_do_arquivo(RAIZ_ESTOQUE / "aplicacao" / "servico.py")

    assert not any("repositorio" in modulo for modulo in imports)
    assert "estoque.aplicacao.portas" in imports


def test_apresentacao_nao_executa_sql_nem_importa_infraestrutura():
    proibidos = ("estoque.infraestrutura", "sqlite3")

    for arquivo in _arquivos("apresentacao"):
        for modulo in _imports_do_arquivo(arquivo):
            assert not _pertence(modulo, proibidos), (
                f"{arquivo.name} importa {modulo}, violando a fronteira da apresentação"
            )


def test_fachada_publica_nao_expoe_detalhes_do_sqlite():
    import estoque

    for simbolo in ("RepositorioEstoque", "criar_conexao", "criar_tabelas"):
        assert not hasattr(estoque, simbolo)
        assert simbolo not in estoque.__all__

    assert "RepositorioEstoquePorta" in estoque.__all__
