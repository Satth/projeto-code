"""Funções pequenas de validação compartilhadas pelo domínio.

Elas concentram a conversão e a checagem dos valores que entram nos
objetos de domínio. A mensagem de erro é sempre clara para quem usa a
aplicação e para os testes.
"""

from decimal import Decimal, InvalidOperation

from .erros import DadosInvalidos

CENTAVOS = Decimal("0.01")
TIPOS_MOVIMENTACAO = ("entrada", "saida", "ajuste")


def validar_texto(valor, campo):
    """Devolve o texto sem espaços nas pontas ou levanta ``DadosInvalidos``."""
    if not isinstance(valor, str):
        raise DadosInvalidos(f"{campo} deve ser um texto")
    texto = valor.strip()
    if not texto:
        raise DadosInvalidos(f"{campo} não pode ser vazio")
    return texto


def converter_preco(valor, campo="preço unitário"):
    """Converte um preço para ``Decimal`` com exatamente duas casas.

    Aceita ``Decimal``, inteiro, ``float`` e texto. ``float`` é convertido
    pelo seu texto para reduzir o efeito da representação binária, mas o
    uso de ``Decimal`` continua sendo o recomendado no domínio.
    """
    if isinstance(valor, bool):
        raise DadosInvalidos(f"{campo} deve ser um número maior que zero")

    if isinstance(valor, Decimal):
        preco = valor
    elif isinstance(valor, int):
        preco = Decimal(valor)
    elif isinstance(valor, float):
        preco = Decimal(str(valor))
    elif isinstance(valor, str):
        try:
            preco = Decimal(valor.strip())
        except InvalidOperation as erro:
            raise DadosInvalidos(f"{campo} inválido: {valor!r}") from erro
    else:
        raise DadosInvalidos(f"{campo} deve ser um número maior que zero")

    if not preco.is_finite() or preco <= 0:
        raise DadosInvalidos(f"{campo} deve ser maior que zero")

    try:
        preco_com_duas_casas = preco.quantize(CENTAVOS)
    except InvalidOperation as erro:
        raise DadosInvalidos(f"{campo} inválido: {valor!r}") from erro

    if preco != preco_com_duas_casas:
        raise DadosInvalidos(f"{campo} deve ter no máximo duas casas decimais")

    return preco_com_duas_casas


def validar_inteiro(valor, campo, *, minimo=0):
    """Garante que o valor é um ``int`` (não ``bool``) e respeita o mínimo."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise DadosInvalidos(f"{campo} deve ser um número inteiro")
    if valor < minimo:
        raise DadosInvalidos(f"{campo} não pode ser menor que {minimo}")
    return valor


def validar_quantidade_positiva(valor, campo="quantidade"):
    """Valida uma quantidade que precisa ser maior que zero."""
    quantidade = validar_inteiro(valor, campo, minimo=0)
    if quantidade == 0:
        raise DadosInvalidos(f"{campo} deve ser maior que zero")
    return quantidade


def validar_observacao(valor):
    """Normaliza a observação opcional de uma movimentação."""
    if valor is None:
        return ""
    if not isinstance(valor, str):
        raise DadosInvalidos("observação deve ser um texto")
    return valor.strip()


def validar_tipo_movimentacao(valor):
    """Garante que o tipo pertence ao contrato de movimentações."""
    if not isinstance(valor, str) or valor not in TIPOS_MOVIMENTACAO:
        tipos = ", ".join(TIPOS_MOVIMENTACAO)
        raise DadosInvalidos(f"tipo de movimentação deve ser um de: {tipos}")
    return valor
