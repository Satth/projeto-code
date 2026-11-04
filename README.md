# Projeto de Controle de Estoque

## 1. Visão geral

Este repositório contém uma aplicação acadêmica de controle de estoque
desenvolvida em Python, com persistência em SQLite e interface de terminal.
O projeto evoluiu de exercícios isolados da disciplina de Análise e
Desenvolvimento de Sistemas para uma implementação integrada organizada em
camadas.

A versão atual prioriza três pontos:

- regras de negócio explícitas e testáveis no domínio;
- dependências apontando para dentro, sem a aplicação conhecer SQLite;
- uma árvore pequena, coerente e fácil de navegar.

Não há API REST, interface web ou interface gráfica nesta etapa.

## 2. Objetivo e funcionalidades

O sistema controla produtos, o saldo disponível e o histórico de
movimentações de estoque. As funcionalidades são:

- cadastrar produtos com nome, preço unitário, saldo inicial e estoque mínimo;
- listar e buscar produtos;
- atualizar nome, preço e estoque mínimo sem alterar o saldo;
- remover produtos que ainda não possuem histórico;
- registrar entradas, saídas e ajustes de inventário;
- consultar o histórico por produto ou de todos os produtos;
- listar produtos abaixo do estoque mínimo;
- manter os dados em um arquivo SQLite entre execuções.

## 3. Arquitetura e responsabilidades das camadas

O pacote `estoque` é dividido em quatro camadas com responsabilidades
distintas.

| Camada | Diretório | Responsabilidade |
| --- | --- | --- |
| Domínio | `estoque/dominio/` | Entidade `Produto`, movimentações, validações e exceções de negócio. Não importa SQLite, aplicação ou apresentação. |
| Aplicação | `estoque/aplicacao/` | Casos de uso do `ServicoEstoque`, modelos de resultado e a porta `RepositorioEstoquePorta`. |
| Infraestrutura | `estoque/infraestrutura/sqlite/` | Conexão, schema e implementação SQLite do contrato de repositório. |
| Apresentação | `estoque/apresentacao/` | Menu, leitura de entradas, formatação e mensagens da CLI. Não executa SQL. |

O ponto de entrada `estoque/__main__.py` é apenas composição: escolhe o
caminho do banco, abre a conexão, cria as tabelas, instancia o repositório,
injeta-o no serviço, inicia a CLI e fecha a conexão.

### Direção das dependências

```text
apresentacao
     |
     v
aplicacao ------> portas (Protocol)
     |
     v
dominio

infraestrutura.sqlite
     |
     +---- implementa as portas da aplicacao
     |
     +---- utiliza o dominio e os modelos da aplicacao

__main__.py
     |
     +---- compoe aplicacao, infraestrutura e apresentacao
```

Regras aplicadas:

- `dominio` não depende de nenhuma outra camada interna.
- `aplicacao` depende do domínio e dos próprios contratos em `portas.py`.
- `servico.py` não importa `sqlite3`, `RepositorioEstoque` nem o módulo
  concreto de repositório.
- `infraestrutura.sqlite` pode importar domínio e modelos da aplicação.
- `apresentacao` conversa com o serviço e trata as exceções de domínio.
- A fachada `estoque/__init__.py` expõe domínio, aplicação e a porta, mas
  não exporta a implementação SQLite.

### Contrato de persistência

`estoque/aplicacao/portas.py` define `RepositorioEstoquePorta` com
`typing.Protocol`. O contrato reúne apenas as operações usadas pelo
serviço: salvar, buscar, listar, verificar nome, atualizar, remover,
aplicar movimentação e listar movimentações.

`estoque/aplicacao/modelos.py` contém `ProdutoComId` e
`MovimentacaoRegistrada`. Esses modelos de resultado não pertencem mais à
infraestrutura.

## 4. Árvore de diretórios

```text
projeto-code/
├── .github/
│   └── workflows/
│       └── testes.yml
├── estoque/
│   ├── __init__.py
│   ├── __main__.py
│   ├── dominio/
│   │   ├── __init__.py
│   │   ├── erros.py
│   │   ├── movimentacao.py
│   │   ├── produto.py
│   │   └── validacao.py
│   ├── aplicacao/
│   │   ├── __init__.py
│   │   ├── modelos.py
│   │   ├── portas.py
│   │   └── servico.py
│   ├── infraestrutura/
│   │   ├── __init__.py
│   │   └── sqlite/
│   │       ├── __init__.py
│   │       ├── banco.py
│   │       └── repositorio.py
│   └── apresentacao/
│       ├── __init__.py
│       └── cli.py
├── tests/
│   ├── conftest.py
│   ├── test_arquitetura.py
│   ├── test_movimentacao.py
│   ├── test_persistencia.py
│   ├── test_produto.py
│   ├── test_repositorio.py
│   ├── test_servico.py
│   └── test_servico_simulado.py
├── .gitignore
├── pytest.ini
├── requirements-dev.txt
└── README.md
```

## 5. Fluxo de execução

1. `python -m estoque` executa `estoque/__main__.py`.
2. O ponto de entrada lê `ESTOQUE_DB` ou usa `estoque.db`.
3. `criar_conexao()` configura o SQLite e `criar_tabelas()` garante o schema.
4. `RepositorioEstoque` é instanciado com a conexão.
5. O repositório é injetado em `ServicoEstoque`.
6. `apresentacao/cli.py` inicia o menu e chama os casos de uso.
7. Ao sair, a conexão é fechada no bloco `finally`.

Fluxo de uma movimentação:

```text
CLI
 |
 v
ServicoEstoque.dar_entrada / dar_saida / ajustar
 |
 +--> dominio: Entrada / Saida / Ajuste aplicam a regra ao Produto
 |
 +--> RepositorioEstoquePorta.aplicar_movimentacao
          |
          v
      SQLite: atualiza o saldo e grava o histórico na mesma transação
```

## 6. Regras de negócio

### Produto

- O nome deve ser um texto não vazio; espaços nas pontas são removidos.
- O preço unitário deve ser maior que zero e ter no máximo duas casas
  decimais.
- Quantidade e quantidade mínima devem ser inteiros não negativos. `bool`
  não é aceito como inteiro.
- O saldo nunca pode ficar negativo.
- Uma saída maior que o saldo disponível levanta `EstoqueInsuficiente` e
  não altera o estado.
- `abaixo_do_minimo()` usa a comparação estrita
  `quantidade < quantidade_minima`; estar exatamente no mínimo não gera
  alerta.

### Movimentações

- Entradas e saídas exigem quantidade inteira estritamente positiva.
- Ajustes definem um saldo absoluto inteiro não negativo.
- A coerência aritmética é conferida antes da escrita: entrada exige
  `novo = anterior + quantidade`, saída exige
  `novo = anterior - quantidade` e ajuste exige
  `quantidade = novo saldo`.
- Movimentações incoerentes levantam `MovimentacaoInconsistente`; dados
  malformados levantam `DadosInvalidos`.
- Nenhuma rejeição altera o saldo ou grava histórico.

### Nomes duplicados

O nome do produto é único. A comparação do SQLite usa `COLLATE NOCASE`,
então `Teclado`, `teclado` e `TECLADO` são considerados o mesmo nome para
fins de unicidade. A apresentação preserva a grafia cadastrada.

### Cadastro, atualização e remoção

- O saldo informado no cadastro é o saldo inicial e não gera linha de
  histórico.
- A atualização altera nome, preço e quantidade mínima. O saldo só muda
  por movimentação.
- Um produto com movimentações não pode ser removido enquanto o histórico
  existir. A chave estrangeira usa `ON DELETE RESTRICT` e a operação
  levanta `ProdutoComMovimentacoes`.
- Um produto sem histórico pode ser removido normalmente.

### Histórico

Cada movimentação registra produto, tipo (`entrada`, `saida` ou `ajuste`),
quantidade informada, quantidade anterior, quantidade nova, observação
opcional e data/hora em UTC.

Para entrada e saída, a coluna `quantidade` representa as unidades
movimentadas. Para ajuste, representa o novo saldo absoluto; os campos de
quantidade anterior e nova tornam a operação explícita.

## 7. Persistência e banco de dados

### Local do banco

Por padrão, o arquivo é criado como `estoque.db` no diretório de onde o
comando é executado. A CLI imprime o caminho absoluto ao iniciar.

Para usar outro arquivo:

```powershell
# PowerShell
$env:ESTOQUE_DB = "C:\Users\Usuario\Documents\estoque-demo.db"
python -m estoque
```

```bash
# Bash
ESTOQUE_DB=/caminho/estoque-demo.db python -m estoque
```

O banco local não deve ser versionado. O `.gitignore` exclui `*.db`,
`*.sqlite`, `*.sqlite3`, arquivos auxiliares do SQLite, caches e ambientes
virtuais.

### Tabelas

```text
produtos
  id, nome (unico, NOCASE), preco_unitario, quantidade, quantidade_minima

movimentacoes
  id, produto_id, tipo, quantidade,
  quantidade_anterior, quantidade_nova, observacao, criado_em
```

O preço é armazenado como texto e convertido de volta para `Decimal` no
repositório, evitando que o valor atravesse a persistência como `float`.

O schema mantém as seguintes restrições:

- `produtos.quantidade >= 0` e `produtos.quantidade_minima >= 0`;
- `movimentacoes.tipo` restrito a `entrada`, `saida` e `ajuste`;
- `movimentacoes.quantidade_anterior >= 0` e
  `movimentacoes.quantidade_nova >= 0`;
- chave estrangeira de `movimentacoes.produto_id` para `produtos.id` com
  `ON DELETE RESTRICT`.

O schema **não** possui `CHECK` de quantidade positiva para movimentações.
Essa regra, assim como a coerência aritmética, é validada pelo repositório
Python antes da escrita.

### Transações e concorrência

A movimentação atualiza o saldo e insere o histórico dentro do mesmo bloco
`with conexao`. Se a inserção do histórico falhar, o SQLite desfaz também a
atualização da quantidade.

A atualização do saldo é condicional: usa `WHERE id = ? AND quantidade = ?`
com o saldo lido pelo serviço. Se o saldo mudar antes da gravação, nenhuma
linha é atualizada, a operação levanta `SaldoDesatualizado` e o histórico
não é gravado. Isso detecta a corrida, mas não transforma a aplicação em um
sistema multiusuário com controle de concorrência completo.

### Persistência entre execuções

Fechar a aplicação não apaga o arquivo. Na próxima execução,
`criar_tabelas()` apenas garante que as tabelas existam; os produtos e o
histórico já gravados são lidos novamente. O teste
`tests/test_persistencia.py` comprova isso abrindo uma conexão, cadastrando
e movimentando um produto, fechando a conexão e abrindo outra para o mesmo
arquivo.

### Isolamento nos testes

A fixture `conexao` em `tests/conftest.py` cria um arquivo dentro de
`tmp_path` para cada teste. Assim, um teste não vê os dados de outro e o
banco local `estoque.db` do desenvolvedor não é usado nem contaminado.

## 8. Instalação e configuração

### 1. Criar e ativar o ambiente virtual

No PowerShell (Windows):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

No Bash/Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalar as dependências

```bash
python -m pip install -r requirements-dev.txt
```

A aplicação usa apenas a biblioteca padrão, incluindo `sqlite3`, `decimal`,
`abc`, `dataclasses` e `typing`. A única dependência externa é o `pytest`,
necessário para a suíte de testes.

## 9. Como executar a aplicação

Na raiz do projeto, com o ambiente virtual ativado:

```bash
python -m estoque
```

O menu oferece:

```text
1 - Listar produtos
2 - Cadastrar produto
3 - Registrar entrada
4 - Registrar saída
5 - Ajustar quantidade
6 - Ver histórico
7 - Produtos abaixo do mínimo
8 - Atualizar produto
9 - Remover produto
0 - Sair
```

Exemplo de uso:

1. cadastre um produto com preço `150.00`, quantidade inicial `10` e
   mínimo `5`;
2. registre uma entrada de `2` unidades;
3. registre uma saída de `3` unidades;
4. abra o histórico e confira `10 -> 12` e `12 -> 9`;
5. saia e execute `python -m estoque` novamente: o produto e o histórico
   continuam no arquivo `estoque.db`.

A remoção é recusada quando o produto já possui histórico, para preservar
as movimentações.

## 10. Como executar os testes

```bash
python -m pytest -v
```

O `pytest.ini` declara explicitamente o diretório da suíte e a raiz do
projeto:

```ini
[pytest]
testpaths = tests
pythonpath = .
```

Exemplos de execução parcial:

```bash
python -m pytest tests/test_servico.py -v
python -m pytest tests/test_repositorio.py -v
python -m pytest tests/test_persistencia.py -v
python -m pytest tests/test_arquitetura.py -v
```

Na validação local desta refatoração, **144 casos de teste passaram** em
Python 3.12.14 com pytest 9.2.0. Desses, 10 são testes novos: 5 verificam
as fronteiras arquiteturais e 5 comprovam o contrato de repositório,
inclusive com uma implementação simulada em memória.

A suíte cobre, entre outros pontos:

- criação de produto válido e rejeição de nome, preço e quantidades
  inválidos;
- entrada, saída válida e saída acima do disponível;
- estoque mínimo, inclusive o limite exato;
- cadastro, busca, listagem, atualização e remoção;
- produto inexistente e nome duplicado sem diferenciar maiúsculas de
  minúsculas;
- registro de entradas, saídas e ajustes no histórico;
- persistência depois de fechar e reabrir uma conexão com o arquivo
  SQLite;
- reversão transacional quando a gravação do histórico falha;
- validação defensiva de id, tipo, saldos, quantidade e observação na
  fronteira do repositório;
- rejeição de entrada, saída e ajuste aritmeticamente incoerentes;
- detecção de saldo desatualizado sem gravação de histórico;
- preservação das invariantes após operações inválidas;
- tradução específica da restrição de remoção, sem mascarar outros erros de
  integridade;
- ausência de dependências proibidas entre domínio, aplicação,
  apresentação e infraestrutura;
- funcionamento do serviço com um repositório simulado, sem SQLite.

## 11. Integração contínua

O workflow `.github/workflows/testes.yml` executa em `push` e
`pull_request`:

```text
checkout do repositório (actions/checkout@v7)
        |
configuração do Python 3.12 (actions/setup-python@v7)
        |
instalação de requirements-dev.txt
        |
python -m pytest -v
```

O workflow usa `ubuntu-latest`, Python 3.12 e as versões v7 das actions de
checkout e configuração do Python. Ele não depende da estrutura antiga de
pastas: a configuração `testpaths = tests` mantém a execução restrita à
suíte principal.

Esta branch de refatoração não foi publicada no remoto. Portanto, não há
resultado de CI remoto para ela; os resultados apresentados neste documento
são exclusivamente da execução local descrita na seção anterior.

## 12. Limitações técnicas conhecidas

- A aplicação é local e mono-usuário. A gravação condicional detecta que o
  saldo mudou desde a leitura e recusa a movimentação, mas isso não
  substitui um controle de concorrência multiusuário.
- `COLLATE NOCASE` do SQLite ignora maiúsculas e minúsculas para caracteres
  ASCII. Nomes acentuados podem não ser tratados como duplicados em
  variações de caixa; uma normalização Unicode explícita seria necessária.
- O saldo inicial do cadastro não gera uma linha de histórico; ele é o
  ponto de partida do produto.
- Não há migrações de schema nem rotina de backup. O schema não foi
  alterado nesta refatoração. O arquivo SQLite deve ser preservado pelo
  usuário.
- A remoção de produto com histórico é bloqueada de propósito para não
  apagar o rastro das movimentações.
- Não há API REST, interface web ou interface gráfica nesta etapa.
- A porta de repositório é específica para o estoque. Ela não é uma
  hierarquia genérica de interfaces e deve evoluir apenas quando um novo
  caso de uso exigir uma operação concreta.
