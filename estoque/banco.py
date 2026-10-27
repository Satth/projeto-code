"""Configuração do SQLite e criação do schema do controle de estoque."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nome              TEXT NOT NULL COLLATE NOCASE UNIQUE,
    preco_unitario    TEXT NOT NULL,
    quantidade        INTEGER NOT NULL CHECK (quantidade >= 0),
    quantidade_minima INTEGER NOT NULL CHECK (quantidade_minima >= 0)
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id          INTEGER NOT NULL,
    tipo                TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida', 'ajuste')),
    quantidade          INTEGER NOT NULL,
    quantidade_anterior INTEGER NOT NULL CHECK (quantidade_anterior >= 0),
    quantidade_nova     INTEGER NOT NULL CHECK (quantidade_nova >= 0),
    observacao          TEXT NOT NULL DEFAULT '',
    criado_em           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_movimentacoes_produto
    ON movimentacoes (produto_id, id);
"""


def criar_conexao(caminho="estoque.db"):
    """Abre (ou cria) o banco e devolve uma conexão configurada.

    O preço é armazenado como texto para preservar exatamente o valor
    decimal; a conversão de volta para ``Decimal`` é feita no repositório.
    """
    conexao = sqlite3.connect(Path(caminho))
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas(conexao):
    """Cria as tabelas e o índice que ainda não existirem."""
    conexao.executescript(SCHEMA)
