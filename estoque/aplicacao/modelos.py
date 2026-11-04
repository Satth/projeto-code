"""Modelos de resultado usados pela camada de aplicação.

Eles representam dados já prontos para circulação entre casos de uso e
apresentação. Não contêm SQL nem conhecem a implementação de persistência.
"""

from dataclasses import dataclass

from ..dominio.produto import Produto


@dataclass(frozen=True)
class ProdutoComId:
    """Produto do domínio acompanhado do identificador gerado pelo banco."""

    id: int
    produto: Produto

    @property
    def nome(self):
        return self.produto.nome

    @property
    def quantidade(self):
        return self.produto.quantidade


@dataclass(frozen=True)
class MovimentacaoRegistrada:
    """Uma linha do histórico, já convertida para um objeto legível."""

    id: int
    produto_id: int
    produto_nome: str
    tipo: str
    quantidade: int
    quantidade_anterior: int
    quantidade_nova: int
    observacao: str
    criado_em: str
