# Busca-de-CNPJ-para-CRM
Este projeto automatiza a busca de informações de empresas a partir do nome da startup/empresa do Brasil


A partir de uma lista de nomes de empresas em um arquivo CSV, o script busca informações públicas na internet, tenta identificar o CNPJ da empresa e consulta dados cadastrais para retornar endereço, cidade, estado, CEP e país.

## Objetivo

O objetivo do projeto é reduzir o trabalho manual na busca de informações de empresas, principalmente dados de endereço, para uso em processos de cadastro, enriquecimento ou atualização de contas no CRM.

## O que o projeto faz

- Lê uma lista de empresas/startups a partir de um arquivo CSV.
- Identifica automaticamente a coluna com o nome da empresa.
- Busca site e CNPJ usando a SerpAPI.
- Consulta dados cadastrais do CNPJ na API pública CNPJ.ws.
- Gera um arquivo final em CSV com as informações encontradas.
- Retorna dados úteis para cadastro no CRM, como:
  - nome da empresa;
  - site;
  - CNPJ;
  - rua/logradouro;
  - cidade;
  - estado;
  - CEP;
  - país;
  - status da busca.

## Arquivos do projeto
.
├── enriquecer_startups.py
├── startups.csv
├── README.md
└── script.txt
