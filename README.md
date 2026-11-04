# Projeto de Controle de Estoque

<div align="center">

**Aplicação de controle de estoque desenvolvida em Python, com interface de terminal, persistência em SQLite e arquitetura modular organizada em camadas.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pytest](https://img.shields.io/badge/Tests-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![GitHub Actions](https://github.com/Satth/projeto-code/actions/workflows/testes.yml/badge.svg)](https://github.com/Satth/projeto-code/actions/workflows/testes.yml)

</div>

---

## Sobre

O **Projeto de Controle de Estoque** é uma aplicação desenvolvida em Python para gerenciar produtos, acompanhar quantidades disponíveis e registrar movimentações de estoque.

O sistema utiliza SQLite para persistência dos dados e uma interface de linha de comando (CLI) para interação com o usuário.

A arquitetura separa as responsabilidades em quatro camadas: domínio, aplicação, infraestrutura e apresentação. Essa organização facilita a manutenção, os testes e a evolução do sistema.

## Funcionalidades

### Produtos
- Cadastro de produtos com nome, preço e quantidades.
- Consulta e listagem de produtos.
- Atualização de informações sem alterar o saldo.
- Remoção de produtos sem histórico de movimentações.
- Identificação de produtos abaixo do estoque mínimo.

### Movimentações
- Registro de entradas e saídas de estoque.
- Ajustes de inventário.
- Consulta do histórico de movimentações.
- Validação de quantidades e saldos.
- Proteção contra movimentações inconsistentes e saldos desatualizados.

### Persistência
- Armazenamento dos dados em SQLite.
- Histórico preservado entre execuções.
- Atualização do saldo e registro da movimentação na mesma transação.

---

## Instalação e execução

### 1. Clonar o repositório

```bash
git clone https://github.com/Satth/projeto-code.git
cd projeto-code
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

Ative o ambiente virtual conforme seu terminal.

**Git Bash (Windows):**

```bash
source .venv/Scripts/activate
```

**PowerShell (Windows):**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements-dev.txt
```

A aplicação utiliza recursos da biblioteca padrão do Python. O `pytest` é a dependência externa necessária para executar os testes.

### 4. Executar a aplicação

Na raiz do projeto:

```bash
python -m estoque
```

A aplicação utiliza `estoque.db` como banco de dados padrão. O caminho pode ser personalizado pela variável de ambiente `ESTOQUE_DB`.

---

## Testes

O projeto utiliza **pytest** para validar as regras de negócio, os serviços, a persistência e os limites entre as camadas da aplicação.

Para executar toda a suíte:

```bash
python -m pytest -v
```

Os testes cobrem:

- Validações de produtos e movimentações;
- Operações de cadastro, consulta, atualização e remoção;
- Integridade dos saldos e do histórico;
- Persistência em SQLite;
- Regras de dependência entre as camadas;
- Funcionamento da aplicação com um repositório simulado.

O projeto também possui integração contínua com GitHub Actions, que executa os testes automaticamente em eventos de `push` e `pull_request`.

---

## Arquitetura

A aplicação está organizada em quatro camadas, cada uma com uma responsabilidade específica.

| Camada | Responsabilidade |
| --- | --- |
| **Domínio** | Entidades, regras de negócio, validações e exceções. |
| **Aplicação** | Casos de uso, serviços, modelos e contratos de persistência. |
| **Infraestrutura** | Conexão com SQLite e implementação do repositório. |
| **Apresentação** | Interface de terminal, entradas e mensagens ao usuário. |

### Organização das dependências

```text
        Apresentação
              |
              v
          Aplicação
              |
              v
           Domínio

       Infraestrutura
              |
              v
       Implementa os
       contratos da
         Aplicação

          __main__
              |
              v
       Composição das
          camadas
```

O serviço da aplicação depende de um contrato de repositório, não diretamente do SQLite. Isso permite utilizar diferentes implementações de persistência sem alterar as regras de negócio.

---

## Estrutura do projeto

```text
projeto-code/
├── .github/
│   └── workflows/
│       └── testes.yml
│
├── estoque/
│   ├── dominio/
│   ├── aplicacao/
│   ├── infraestrutura/
│   │   └── sqlite/
│   ├── apresentacao/
│   ├── __init__.py
│   └── __main__.py
│
├── tests/
│
├── .gitignore
├── pytest.ini
├── requirements-dev.txt
└── README.md
```

---

## Tecnologias

| Tecnologia | Utilização |
| --- | --- |
| Python 3.12 | Linguagem principal e ambiente de CI. |
| SQLite | Persistência dos dados. |
| pytest | Testes automatizados. |
| Git | Controle de versão. |
| GitHub | Hospedagem do código. |
| GitHub Actions | Integração contínua. |

---

<div align="center">

<sub>Python · SQLite · Arquitetura em Camadas · Pytest · Git · GitHub Actions</sub>

</div>