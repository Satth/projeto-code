# Refatoracao do relatorio de vendas

## As duas versoes

### Versao procedural

A versao inicial percorria as vendas com um laco for, verificava o valor minimo, calculava o valor liquido e acumulava o resultado por categoria.

### Versao funcional

A versao final separa as responsabilidades em funcoes e utiliza um pipeline com filter, map e reduce.

A funcao acima_do_minimo seleciona as vendas validas, aplicar_imposto calcula o valor liquido conforme a categoria e agrupar_por_categoria soma os valores por categoria.

## Tempo gasto

- Escrever os testes: nao cronometrado pela equipe.
- Separar as tres funcoes: nao cronometrado pela equipe.
- Aplicar a mudanca de imposto por categoria: nao cronometrado pela equipe.

## Qual versao a equipe leva para o projeto do semestre

A equipe leva a versao funcional para o projeto do semestre.
A separacao das responsabilidades facilita a criacao e a manutencao dos testes.
O uso de filter, map e reduce deixa explicita a sequencia de transformacoes.
A mudanca do imposto por categoria pode ser feita em aplicar_imposto sem alterar relatorio.
Os testes permitem verificar as regras do relatorio por comportamento.

## O que ficou em duvida

Uma duvida da equipe e como decidir, em projetos maiores, quando uma solucao funcional com filter, map e reduce continua mais legivel do que uma implementacao procedural tradicional com um laco.
