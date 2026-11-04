"""Contrato das dependências de persistência da aplicação.

O serviço depende apenas desta porta. A implementação SQLite fica em
``estoque.infraestrutura.sqlite`` e qualquer outra implementação que
atenda ao mesmo conjunto de operações pode ser injetada.
"""

from typing import Protocol, runtime_checkable

from ..dominio.produto import Produto
from .modelos import MovimentacaoRegistrada, ProdutoComId


@runtime_checkable
class RepositorioEstoquePorta(Protocol):
    """Operações de repositório exigidas pelos casos de uso do estoque."""

    def salvar(self, produto: Produto) -> int:
        """Persiste um produto novo e devolve o identificador gerado."""

    def buscar(self, produto_id: int) -> Produto | None:
        """Devolve o produto ou ``None`` quando o identificador não existe."""

    def listar(self) -> list[ProdutoComId]:
        """Lista os produtos em ordem de cadastro."""

    def existe_nome(self, nome: str, exceto_id: int | None = None) -> bool:
        """Informa se o nome já está em uso, ignorando opcionalmente um id."""

    def atualizar(self, produto_id: int, produto: Produto) -> bool:
        """Atualiza os dados cadastrais e informa se houve alteração."""

    def remover(self, produto_id: int) -> bool:
        """Remove o produto e informa se houve remoção."""

    def aplicar_movimentacao(
        self,
        produto_id: int,
        quantidade_anterior: int,
        nova_quantidade: int,
        tipo: str,
        quantidade: int,
        observacao: str,
    ) -> None:
        """Atualiza o saldo e grava o histórico na mesma transação."""

    def listar_movimentacoes(
        self, produto_id: int | None = None
    ) -> list[MovimentacaoRegistrada]:
        """Devolve o histórico completo ou o de um produto específico."""
