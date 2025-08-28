# Laboratório 1 

Este projeto consiste na análise das principais características de repositórios populares open-source. 

## Como rodar o projeto

### 1. Gerar um Token de Acesso no GitHub

Acesse as configurações do seu GitHub e gere um Personal Access Token com as permissões necessárias.

### 2. Baixar o projeto

```bash
git clone https://github.com/phmoreiraf/Lab---Experimentacao-de-Software.git
cd https://github.com/phmoreiraf/Lab---Experimentacao-de-Software/lab-01/code
```

### 3. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 4. Ativar o ambiente virtual

```bash
.venv\Scripts\activate    # Windows
```

### 5. Instalar dependências

```bash
pip install -r requirements.txt
```

### 6. Configurar o token no código

1. Configure seu token de acesso do GitHub.
2. Crie um arquivo .env na pasta ```code```
3. Copie seu token do github no arquivo criado.

### 7. Executar o script

```bash
python main.py
```

### 8. Navegue pelo menu

O menu da aplicação tem três opções:

1. Buscar dados dos repositórios mais populares -> Busca os dados brutos do github e os salva na pasta ```data``` em um arquivo csv (já terá dados disponíveis, então use essa opção se quiser dados mais recentes).

2. Analisar dados -> Verifica quais dados estão na pasta ```data``` e apresenta as opções para o usuário. Ao escolher um conjunto de dados é feito uma analise estatistica simples das tendência central , moda, média, mediana que são mostradas ao usuário e gerado gráficos na pasta ```charts```.

3. Sair -> Sai do programa.

## Objetivos

As métricas obtidas buscam responder seis questões de pesquisa principais e uma questão bônus, sendo elas:

### Questões de Pesquisa (RQ)

- **RQ 01:** Sistemas populares são maduros/antigos?
- **RQ 02:** Sistemas populares recebem muita contribuição externa?
- **RQ 03:** Sistemas populares lançam releases com frequência?
- **RQ 04:** Sistemas populares são atualizados com frequência?
- **RQ 05:** Sistemas populares são escritos nas linguagens mais populares?
- **RQ 06:** Sistemas populares possuem um alto percentual de issues fechadas?
- **RQ 07:** Sistemas escritos em linguagens mais populares recebem mais contribuição *(questão bônus)*

Com essas respostas, será possível definir características presentes em projetos populares, aumentando o conhecimento sobre o que é necessário para que um repositório tenha sucesso atualmente.

### Hipoteses Informais

Tendo em vista as questões de pesquisa apresentadas, foram formuladas algumas hipoteses informais pelo grupo deste projeto. Essas hipoteses trazem o que se espera dos sistemas mais populares partindo do ponto de vista do senso comum. Sendo elas:

- **H01 (RQ01):** Sistemas populares são relativamente antigos, com idade média entre 7–8 anos.
- **H02 (RQ02):** Sistemas populares recebem bastante contribuição externa, com muitos pull requests e colaboradores de fora da equipe principal.
- **H03 (RQ03):** Sistemas populares lançam novas versões com frequência.
- **H04 (RQ04):** Sistemas populares possuem atividade constante, com commits regulares e atualizações frequentes no repositório.
- **H05 (RQ05):** Sistemas populares tendem a ser escritos principalmente em linguagens amplamente utilizadas, especialmente JavaScript, Python e Java.
- **H06 (RQ06):** Sistemas populares possuem um alto percentual de issues resolvidas/fechadas, refletindo boa manutenção.
- **H07 (RQ07):** Projetos escritos em linguagens populares atraem mais contribuições externas do que os escritos em linguagens menos utilizadas.

## Metodologia

Os dados dos repositórios são coletados por meio da API GraphQL do GitHub. Para isso, o projeto é desenvolvido em Python, aproveitando o extenso suporte da linguagem para análise de dados. As ferramentas utilizadas são:

### Ferramentas

- API GraphQL do GitHub - API que providencia dados acerca dos repositórios públicos do github por meio do GraphQL.
- Python 3.12 - Linguagem de programação.
- Requestes - Biblioteca do python que facilita o envio de requisições HTTP
- OS - Biblioteca padrão do python que disponibilita funções para operações de nível de sistema operacional
- Python-dotenv - Biblioteca do python que possibilita o uso de arquivos .env para variavéis de ambiente

Após a coleta das informações inciais, é feito uma sumarização através de valores medianos.

## Resultados

### Métricas coletadas para cada RQ:

#### RQ01 - Idade dos repositorios (anos)
- Mediana: 8.37
- Média: 8.09
- Moda: 12.15

#### RQ02 - Pull Requests Aceitos
- Mediana: 702.0
- Média: 3587.87
- Moda: 1

#### RQ03 - Releases
- Mediana: 35.0
- Média: 109.34
- Moda: 0

#### RQ04 - Dias desde ultima atualizacao 
- Mediana: 7.0
- Média: 7.01
- Moda: 7

#### RQ05 - Linguagens mais usadas 

| Linguagem | Numero de Repositorios |
| ------------- | ------------- |
|Python              |189|
|TypeScript          |156|
|JavaScript          |129|
|Go                  | 73|
|Java                | 50|
|C++                 | 47|
|Rust                | 45|
|C                   | 25|
|Jupyter Notebook    | 22|
|Shell               | 19|
|HTML                | 19|
|Ruby                | 12|
|C#                  | 12|
|Kotlin              | 11|
|Swift               |  9|
|CSS                 |  8|
|PHP                 |  7|
|Vue                 |  7|
|Markdown            |  5|
|Dart                |  5|
|MDX                 |  5|
|Clojure             |  4|
|Vim Script          |  4|
|Zig                 |  3|
|Dockerfile          |  3|
|Assembly            |  2|
|Batchfile           |  2|
|TeX                 |  2|
|Lua                 |  2|
|Scala               |  2|
|Makefile            |  2|
|Roff                |  2|
|Haskell             |  2|
|Svelte              |  2|
|Blade               |  1|
|Nunjucks            |  1|
|Julia               |  1|
|PowerShell          |  1|
|V                   |  1|
|LLVM                |  1|
|Elixir              |  1|
|Objective-C         |  1|
|SCSS                |  1|

#### RQ06 - Percentual de Issues Fechadas -
- Mediana: 86.56
- Média: 79.95
- Moda: 100.0

#### RQ07 - Metricas por Linguagem 
**Linguagens mais populares:**
- Python 
- TypeScript
- JavaScript
- Go
- Java

**Pull Requests Aceitos:** 
- Populares: 927.0
- Outras: 415.0

**Releases:** 
- Populares: 62.0
- Outras: 3.0

**Dias desde ultima atualização:** 
- Populares: 7.0
- Outras: 7.0

