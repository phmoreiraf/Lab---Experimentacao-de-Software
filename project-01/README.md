# Laboratório 1 

Este projeto consiste na análise das principais características de repositórios populares open-source. 

## Objetivos

As métricas obtidas buscam responder seis questões de pesquisa principais e uma questão bônus, sendo elas:

### Questões de Pesquisa (QP)

- **QP 01:** Sistemas populares são maduros/antigos?
- **QP 02:** Sistemas populares recebem muita contribuição externa?
- **QP 03:** Sistemas populares lançam releases com frequência?
- **QP 04:** Sistemas populares são atualizados com frequência?
- **QP 05:** Sistemas populares são escritos nas linguagens mais populares?
- **QP 06:** Sistemas populares possuem um alto percentual de issues fechadas?
- **QP 07:** Sistemas escritos em linguagens mais populares recebem mais contribuição *(questão bônus)*

Com essas respostas, será possível definir características presentes em projetos populares, aumentando o conhecimento sobre o que é necessário para que um repositório tenha sucesso atualmente.

## Metodologia

Os dados dos repositórios são coletados por meio da API GraphQL do GitHub. Para isso, o projeto é desenvolvido em Python, aproveitando o extenso suporte da linguagem para análise de dados. As ferramentas utilizadas são:

### Ferramentas

- API GraphQL do GitHub - API que providencia dados acerca dos repositórios públicos do github por meio do GraphQL.
- Python 3.12 - Linguagem de programação.
- Requestes - Biblioteca do python que facilita o envio de requisições HTTP
- OS - Biblioteca padrão do python que disponibilita funções para operações de nível de sistema operacional
- Python-dotenv - Biblioteca do python que possibilita o uso de arquivos .env para variavéis de ambiente

Após a coleta das informações inciais, é feito uma sumarização através de valores medianos.

