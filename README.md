# Busca-de-CNPJ-para-CRM
Este projeto automatiza a busca de informações de empresas a partir do nome da startup/empresa do Brasil


O script consulta informações públicas na internet, tenta identificar o CNPJ da empresa e depois busca os dados cadastrais para retornar informações úteis para cadastro no CRM.

## O que o projeto faz

- Lê uma lista de startups a partir de um arquivo CSV.
- Busca o site e o CNPJ da empresa.
- Consulta dados cadastrais do CNPJ.
- Retorna endereço, cidade, estado, CEP e país.
- Gera um arquivo final chamado `resultado_final.csv`.

## Arquivo de entrada

O projeto usa um arquivo chamado:

```text
startups.csv
