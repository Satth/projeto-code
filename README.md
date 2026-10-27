# Projeto de Controle de Estoque

Projeto acadêmico desenvolvido pela equipe de Estoque ao longo das atividades da disciplina de Análise e Desenvolvimento de Sistemas (ADS).

O repositório reúne os exercícios das aulas e uma implementação integrada do domínio de estoque em Python. A implementação aplicada usa orientação a objetos, validações de domínio e persistência real em SQLite, sem transformar os exercícios independentes em uma única aplicação.

## Objetivo acadêmico

O objetivo é acompanhar a evolução dos conceitos da disciplina — funções, coleções, testes, orientação a objetos e persistência — aplicando-os a um domínio de controle de estoque.

As pastas `aula02-paradigmas/`, `aula03/`, `aula04/` e `aula06/` preservam as atividades no formato em que foram propostas. A pasta `estoque/` contém a versão integrada e mais completa, usada para demonstrar como os conceitos se combinam em um sistema pequeno.

## Domínio

O sistema controla **produtos** e o **saldo disponível** em estoque. As operações previstas são:

- cadastro de produtos;
- entrada de unidades;
- saída de unidades;
- ajuste de inventário;
- consulta do saldo e do estoque mínimo;
- alerta para produtos abaixo do mínimo;
- histórico persistente das movimentações.

O domínio é de estoque, não de roupas, carrinho de compras ou promoções. O projeto de referência `Satth/loja-roupas` foi consultado apenas como inspiração de organização em camadas e de conceitos de POO.

## Estrutura do repositório

```text
projeto-code/
├── aula02-paradigmas/
│   ├── relatorio.py
│   ├── test_relatorio.py
│   └── REFATORACAO.md
├── aula03/
│   ├── pratica1_variaveis.py
│   ├── pratica2_orcamento.py
│   ├── pratica3_frete.py
│   ├── pratica4_diario.py
│   └── pratica5_comanda.py
├── aula04/
│   ├── comanda.py
│   └── test_comanda.py
├── aula06/
│   ├── exercicio_01_dois_objetos.py
│   ├── exercicio_02_funcao_vira_metodo.py
│   ├── exercicio_03_quebrem_de_proposito.py
│   ├── exercicio_04_atributo_de_classe.py
│   ├── test_exercicio_05_invariante.py
│   └── exercicio_06_property_em_acao.py
├── estoque/
│   ├── __init__.py
│   ├── __main__.py
│   ├── banco.py
│   ├── erros.py
│   ├── movimentacao.py
│   ├── produto.py
│   ├── repositorio.py
│   ├── servico.py
│   └── validacao.py
├── tests/
│   ├── conftest.py
│   ├── test_movimentacao.py
│   ├── test_persistencia.py
│   ├── test_produto.py
│   ├── test_repositorio.py
│   └── test_servico.py
├── .github/
│   └── workflows/
│       └── testes.yml
├── .gitignore
├── pytest.ini
├── requirements-dev.txt
└── README.md
```

### Exercícios independentes

Cada arquivo das pastas de aula continua identificável e executável por conta própria. Os seis exercícios da Aula 6 permanecem separados, sem acentos nos nomes dos arquivos:

```text
exercicio_01_dois_objetos.py
exercicio_02_funcao_vira_metodo.py
exercicio_03_quebrem_de_proposito.py
exercicio_04_atributo_de_classe.py
test_exercicio_05_invariante.py
exercicio_06_property_em_acao.py
```

Eles podem ser executados individualmente, por exemplo:

```bash
python aula06/exercicio_01_dois_objetos.py
python -m pytest aula06/test_exercicio_05_invariante.py -v
```

O arquivo `aula03/pratica5_comanda.py` mantém, de propósito, a saída de estoque sem verificação de disponibilidade. Essa falha faz parte do exercício da aula e **não** deve ser confundida com a implementação integrada. A versão correta da regra está em `estoque/produto.py` e em `estoque/servico.py`.

### Implementação integrada

A pasta `estoque/` é um pacote Python independente das atividades. As responsabilidades estão separadas:

| Arquivo | Responsabilidade |
| --- | --- |
| `estoque/produto.py` | Objeto `Produto`, estado, invariantes e métodos de domínio. |
| `estoque/movimentacao.py` | Contrato abstrato `Movimentacao` e operações `Entrada`, `Saida` e `Ajuste`. |
| `estoque/validacao.py` | Conversão de preços e validações compartilhadas. |
| `estoque/erros.py` | Exceções de negócio do domínio. |
| `estoque/banco.py` | Conexão SQLite, `PRAGMA foreign_keys` e criação do schema. |
| `estoque/repositorio.py` | Conversão entre objetos e registros, CRUD e histórico. |
| `estoque/servico.py` | Regras de negócio, coordenação das operações e exceções. |
| `estoque/__main__.py` | Demonstração interativa no terminal. |

O fluxo da aplicação é:

```text
Demonstração no terminal (__main__.py)
                 |
                 v
        ServicoEstoque (servico.py)
        regras de negócio e exceções
                 |
                 v
     RepositorioEstoque (repositorio.py)
     domínio <-> registros SQLite
                 |
                 v
        SQLite (banco.py + estoque.db)
```

O `ServicoEstoque` não importa `sqlite3` e não escreve SQL. Ele recebe um repositório pronto, o que mantém a possibilidade de trocar a persistência sem espalhar comandos SQL pelo domínio.

## Conceitos de POO demonstrados

| Conceito | Onde aparece |
| --- | --- |
| Classes, instâncias e estado | `Produto`, `Entrada`, `Saida`, `Ajuste`, `ServicoEstoque`, `RepositorioEstoque`. |
| Encapsulamento | Atributos internos com `_`, propriedades com `@property` e setters validadores em `Produto`. A quantidade é somente leitura. |
| Invariantes | Nome não vazio, preço positivo, quantidades inteiras não negativas e proibição de saldo negativo. |
| Métodos de domínio | `repor()`, `retirar()`, `ajustar()`, `abaixo_do_minimo()` e `valor_total` em `Produto`. |
| Composição | O serviço contém um repositório; o produto é composto por seus dados e estado; a movimentação atua sobre um produto. |
| Herança e sobrescrita | `Entrada`, `Saida` e `Ajuste` herdam de `Movimentacao` e sobrescrevem `aplicar()`. |
| Contrato abstrato | `Movimentacao` usa `ABC` e `@abstractmethod` para definir o comportamento esperado. |
| Polimorfismo | `ServicoEstoque._movimentar()` chama `movimentacao.aplicar(produto)` sem conhecer o tipo concreto. |
| Tratamento de exceções | `DadosInvalidos`, `EstoqueInsuficiente`, `ProdutoNaoEncontrado`, `NomeDuplicado` e `ProdutoComMovimentacoes`. |
| Separação de responsabilidades | Domínio, serviço, repositório e banco em módulos distintos. |
| Precisão monetária | `Decimal` no domínio; o preço é gravado como texto no SQLite para não perder precisão. |

Não foram criadas subclasses de `Produto` apenas para demonstrar herança. A abstração escolhida foi a das operações de estoque, que realmente variam entre entrada, saída e ajuste.

## Regras de negócio e validações

### Produto

- O nome deve ser um texto não vazio; espaços nas pontas são removidos.
- O preço unitário deve ser maior que zero e ter no máximo duas casas decimais.
- Quantidade e quantidade mínima devem ser inteiros não negativos. `bool` não é aceito como inteiro.
- O saldo nunca pode ficar negativo.
- Uma saída maior que o saldo disponível levanta `EstoqueInsuficiente` e não altera o estado.
- `abaixo_do_minimo()` usa a comparação estrita `quantidade < quantidade_minima`; portanto, estar exatamente no mínimo **não** gera alerta.

### Nomes duplicados

O nome do produto é único. A comparação do SQLite usa `COLLATE NOCASE`, então `Teclado`, `teclado` e `TECLADO` são considerados o mesmo nome para fins de unicidade. A apresentação preserva a grafia cadastrada.

### Cadastro, atualização e remoção

- O saldo informado no cadastro é o **saldo inicial**. Ele não é registrado como movimentação; a partir daí, entradas, saídas e ajustes são registrados no histórico.
- A atualização altera nome, preço e quantidade mínima. O saldo só muda por movimentação, evitando que uma edição de cadastro apague a relação com o histórico.
- Um produto com movimentações não pode ser removido enquanto o histórico existir. A chave estrangeira usa `ON DELETE RESTRICT`; a operação levanta `ProdutoComMovimentacoes`.
- Um produto sem histórico pode ser removido normalmente.

### Histórico

Cada movimentação registra:

- produto;
- tipo (`entrada`, `saida` ou `ajuste`);
- quantidade informada;
- quantidade anterior;
- quantidade nova;
- observação opcional;
- data e hora em UTC.

Para `entrada` e `saida`, a coluna `quantidade` é o número de unidades movimentadas. Para `ajuste`, ela é o novo saldo absoluto desejado; as colunas de quantidade anterior e nova deixam a operação explícita.

## Persistência com SQLite

A aplicação usa apenas a biblioteca padrão `sqlite3`. Não há banco em memória na execução normal e não há dependência de SQLModel, SQLAlchemy, FastAPI ou de uma API REST.

### Onde o banco fica

Por padrão, o arquivo é criado como `estoque.db` no diretório de onde o comando é executado. A demonstração imprime o caminho absoluto ao iniciar.

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

O banco local não deve ser versionado. O `.gitignore` exclui `*.db`, `*.sqlite`, `*.sqlite3`, arquivos auxiliares do SQLite, caches e ambientes virtuais.

### Tabelas

```text
produtos
  id, nome (único, NOCASE), preco_unitario, quantidade, quantidade_minima

movimentacoes
  id, produto_id, tipo, quantidade,
  quantidade_anterior, quantidade_nova, observacao, criado_em
```

O preço é armazenado como texto e convertido de volta para `Decimal` no repositório. Isso evita que o valor atravesse a camada de persistência como `float`.

### Transações

A operação de movimentação atualiza a quantidade do produto e insere a linha do histórico dentro do mesmo bloco `with conexao`. Se a inserção do histórico falhar, o SQLite desfaz também a atualização da quantidade. Esse comportamento é testado com uma falha injetada no segundo `INSERT`.

### Como os dados sobrevivem

Fechar a demonstração não apaga o arquivo. Na próxima execução, `criar_tabelas()` apenas garante que as tabelas existam; os produtos e o histórico já gravados são lidos novamente. O teste `tests/test_persistencia.py` comprova isso abrindo uma conexão, cadastrando e movimentando um produto, fechando a conexão e abrindo outra conexão para o mesmo arquivo.

### Como os testes isolam o banco

A fixture `conexao` em `tests/conftest.py` cria um arquivo dentro de `tmp_path` para cada teste. Assim, um teste não vê os dados de outro e o banco local `estoque.db` do desenvolvedor não é usado nem contaminado.

## Instalação

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

A aplicação em si não tem dependências externas: usa `sqlite3`, `decimal`, `abc`, `dataclasses` e demais módulos da biblioteca padrão. O `requirements-dev.txt` instala apenas o `pytest`, necessário para a suíte de testes.

## Executar a demonstração

Na raiz do projeto, com o ambiente virtual ativado:

```bash
python -m estoque
```

O menu permite:

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

1. cadastre um produto com preço `150.00`, quantidade inicial `10` e mínimo `5`;
2. registre uma entrada de `2` unidades;
3. registre uma saída de `3` unidades;
4. abra o histórico e confira `10 -> 12` e `12 -> 9`;
5. saia e execute `python -m estoque` novamente: o produto e o histórico continuam no arquivo `estoque.db`.

As opções 8 e 9 atualizam e removem produtos. A remoção é recusada quando o produto já possui histórico, para preservar as movimentações.

Não há interface gráfica nem API REST nesta etapa.

## Executar os testes

```bash
python -m pytest -v
```

O `pytest.ini` define a raiz do projeto no `pythonpath`, permitindo importar o pacote `estoque` mesmo ao executar o `pytest` diretamente.

Exemplos de execução parcial:

```bash
python -m pytest tests/test_servico.py -v
python -m pytest tests/test_persistencia.py -v
python -m pytest aula02-paradigmas/test_relatorio.py -v
```

Na validação local mais recente, **107 casos de teste passaram** em Python 3.14.8 com pytest 9.1.1. Os 11 testes que já existiam foram preservados; os novos testes cobrem o domínio integrado, a persistência real e a correção do relatório da Aula 2.

A suíte cobre, entre outros pontos:

- criação de produto válido e rejeição de nome, preço e quantidades inválidos;
- entrada, saída válida e saída acima do disponível;
- estoque mínimo, inclusive o limite exato;
- cadastro, busca, listagem, atualização e remoção;
- produto inexistente e nome duplicado sem diferenciar maiúsculas de minúsculas;
- registro de entradas, saídas e ajustes no histórico;
- persistência depois de fechar e reabrir uma conexão com o arquivo SQLite;
- reversão transacional quando a gravação do histórico falha;
- preservação das invariantes após operações inválidas.

## Integração contínua

O workflow `.github/workflows/testes.yml` foi preparado para executar em `push` e `pull_request`:

```text
checkout do repositório
        |
configuração do Python 3.12
        |
instalação de requirements-dev.txt
        |
python -m pytest -v
```

O arquivo está apenas no repositório local nesta etapa; nenhuma execução remota, publicação ou merge foi realizada.

## Relatório da Aula 2: categorias e imposto

O problema original era que `aplicar_imposto()` comparava a categoria em minúsculas, enquanto `agrupar_por_categoria()` usava a grafia original como chave. Com isso, `"Tela"` e `"tela"` recebiam a mesma taxa, mas apareciam em grupos separados.

A correção introduz `normalizar_categoria()` em `aula02-paradigmas/relatorio.py`. A função:

1. remove espaços nas pontas;
2. aplica `capitalize()` para gerar uma chave legível;
3. é usada tanto pelo cálculo da taxa quanto pelo agrupamento.

Assim, `"tela"`, `"Tela"`, `"TELA"` e `"  tela  "` resultam na mesma chave `"Tela"`. O relatório continua legível para o usuário e a comparação da taxa usa a forma normalizada em minúsculas.

A fórmula de imposto **não foi alterada**: o código continua calculando `valor * (1 - imposto)`, ou seja, aplicando uma dedução. Não há, nos arquivos existentes, enunciado suficiente para decidir se o exercício esperava uma dedução ou o acréscimo de um imposto. Essa dúvida permanece registrada em `aula02-paradigmas/REFATORACAO.md` e no relatório final da auditoria. A regra só deve ser mudada se o enunciado da disciplina confirmar a intenção.

Os novos testes cobrem categorias com a mesma grafia, capitalização diferente, espaços, múltiplas categorias, lista vazia e vendas abaixo ou exatamente no limite mínimo.

## Limitações e decisões

- A aplicação é local e single-user; não há controle de concorrência entre dois processos alterando o mesmo produto.
- `COLLATE NOCASE` do SQLite ignora maiúsculas e minúsculas para caracteres ASCII. Nomes acentuados podem não ser tratados como duplicados em variações de caixa; uma normalização Unicode explícita seria necessária para esse caso.
- O saldo inicial do cadastro não gera uma linha de histórico; ele é o ponto de partida do produto. Entradas, saídas e ajustes posteriores são registrados.
- Não há migrações de schema nem rotina de backup. O arquivo SQLite deve ser preservado pelo usuário.
- A remoção de produto com histórico é bloqueada de propósito para não apagar o rastro das movimentações.
- Não há API REST, interface web ou interface gráfica nesta etapa.
- O workflow de CI foi criado localmente, mas não foi executado no GitHub nem publicado.

## Equipe

Projeto desenvolvido pela equipe responsável pelo domínio de Estoque: Eduardo Henrique, Matheus, Roberto Soares, Vinicius e Tiago.
