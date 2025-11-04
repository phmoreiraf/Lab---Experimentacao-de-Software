# Laboratório 4 - Visualização e Análise de Dados Públicos sobre Qualidade do Ar no Brasil

## 1. Introdução

A poluição atmosférica é um dos maiores desafios ambientais contemporâneos. Ela impacta diretamente a saúde da população, a sustentabilidade das cidades e a estabilidade climática do planeta. Entre os poluentes mais estudados estão o material particulado fino (PM2.5) e o material particulado inalável (PM10), ambos compostos por pequenas partículas sólidas ou líquidas em suspensão no ar, capazes de penetrar profundamente no sistema respiratório humano.

Nas últimas décadas, a urbanização acelerada, o aumento do tráfego veicular e as queimadas, especialmente nas regiões Centro-Oeste e Norte do Brasil, agravaram a exposição da população a esses poluentes. A Organização Mundial da Saúde (OMS) estima que milhões de mortes anuais estejam relacionadas à má qualidade do ar, sendo uma das principais causas de doenças respiratórias e cardiovasculares. Diante desse cenário, torna-se urgente investigar, de forma sistemática e aberta, a situação da qualidade do ar nas cidades brasileiras, utilizando dados públicos e ferramentas modernas de análise.

O presente trabalho tem como objetivo desenvolver uma base analítica e visual (dashboard BI) para avaliar a qualidade do ar nas capitais brasileiras, com base em dados da plataforma OpenAQ, uma iniciativa global de dados abertos que integra medições de centenas de estações monitoras espalhadas pelo mundo.

A pesquisa adota o modelo GQM (Goal–Question–Metric) para guiar o processo de coleta e análise de dados, garantindo que cada métrica extraída do sistema atenda a uma questão de pesquisa clara e mensurável.

## 2. GQM - Goal, Question, Metric

### **Goal (Objetivo Geral)**

Investigar os padrões espaciais e temporais da qualidade do ar nas capitais brasileiras, identificando tendências, possíveis fatores de influência e comparando os níveis observados com os limites recomendados pela OMS.

#### **Questions (Questões)**

1. **Q1 - Variação Espacial:**
Quais capitais apresentam os maiores valores médios de concentração de PM2.5 e PM10 nos últimos 180 dias?

    - Métrica associada: média e desvio-padrão das concentrações diárias por cidade e parâmetro.
    - Fonte no código: cálculo agregado no processamento diário (dataset.py) e ranking de cidades (analysis_rqs.py).

2. **Q2 - Padrões Temporais e Sazonais:**
Há variações significativas nas concentrações dos poluentes ao longo dos meses, dias da semana ou períodos do dia?

    - Métrica associada: séries temporais agregadas por mês, dia da semana e hora local (a ser implementado na coleta).
    - Fonte no código: criação da dimensão temporal (dim_time.csv) com campos adicionais month_name, dow_name, hour.

3. **Q3 - Excedência dos Limites da OMS:**
Qual é o percentual de dias em que os níveis de PM2.5 e PM10 ultrapassam os limites seguros definidos pela OMS (15 µg/m³ e 45 µg/m³, respectivamente)?

    - Métrica associada: contagem de dias acima do limite e taxa percentual de excedência por cidade e parâmetro.
    - Fonte no código: função de agregação e cálculo de excedência (analysis_rqs.py).

Essas três perguntas estruturam a análise principal, orientando a coleta, o pré-processamento e as visualizações que serão construídas no dashboard de BI.

## 3. Metodologia e Descrição da Base de Dados

A metodologia foi estruturada em quatro etapas principais - coleta, pré-processamento, consolidação de métricas (GQM) e modelagem para BI, todas automatizadas no código Python, permitindo replicabilidade e atualização contínua dos dados.

**3.1 Etapa 1 - Coleta de Dados Públicos (OpenAQ API)**

Os dados foram obtidos diretamente da API pública v3 do OpenAQ — um repositório global de medições atmosféricas.
A coleta foi realizada por meio de chamadas HTTP aos endpoints:

- Lista de estações no Brasil

    https://api.openaq.org/v3/locations?countries_id=45


Esse endpoint retorna todas as estações de monitoramento ativas no país, incluindo seus sensores, coordenadas e provedores de dados.

- Medições diárias de cada sensor

    https://api.openaq.org/v3/sensors/{sensor_id}/measurements/daily


Permite extrair as médias diárias de concentração dos poluentes monitorados, com parâmetros de data (datetime_from e datetime_to).

A partir dessa base, o estudo considerou apenas as estações localizadas nas capitais brasileiras, definidas manualmente segundo o IBGE.

**3.2 Etapa 2 - Processamento e Limpeza**

O processo de coleta foi implementado em Python, utilizando a biblioteca requests para comunicação com a API e pandas para manipulação e análise dos dados.

O pipeline segue as seguintes etapas:

1. Listagem das estações brasileiras (/locations?countries_id=45);
2. Filtragem das estações pertencentes às capitais brasileiras com base no campo locality ou name;
3. Iteração sobre os sensores disponíveis, selecionando apenas os parâmetros de interesse (PM2.5 e PM10);
4. Coleta das medições diárias de cada sensor nos últimos N dias;
5. Consolidação em um único DataFrame, contendo:

    - Nome da cidade
    - Latitude e longitude
    - Parâmetro medido (PM2.5 ou PM10)
    - Valor médio diário
    - Unidade de medida
    - Data local e UTC

Esses dados são armazenados localmente em CSV (data/raw/openaq_capitais_brasil.csv), servindo como base para análises e visualizações posteriores.

**3.3 Etapa 3 - Métricas e Transformações**

Após a coleta, o código processará os dados para:

- Calcular médias diárias, mensais e anuais por capital e por poluente;
- Identificar capitais com maior média anual de PM2.5 e PM10;
- Gerar gráficos temporais e mapas de calor geográficos;
- Calcular correlações entre latitude/longitude e níveis de poluição.

As métricas serão visualizadas em um dashboard interativo no estilo business intelligence, permitindo a análise comparativa e temporal das capitais.

**3.4 Etapa 4 - Modelagem para BI e Visualização**

Com as métricas consolidadas, os arquivos são exportados para data/bi/ em formato CSV, compondo uma estrutura de esquema estrela para uso em ferramentas de BI (Power BI, Tableau, Looker Studio).
As dimensões incluem:

- dim_city - identificação e coordenadas das capitais;
- dim_time - granularidade temporal (ano, mês, dia, hora, dia da semana);
- dim_parameter - descrição dos poluentes.

A tabela fato (fact_air_quality.csv) contém os valores médios diários e será usada como base principal de visualização.
O dashboard BI será estruturado para representar as três perguntas do GQM em páginas temáticas:

1. Comparativo entre Capitais (Q1);
2. Tendências Temporais (Q2);
3. Excedências aos Limites da OMS (Q3).

Essa abordagem garante coerência entre o modelo conceitual da pesquisa e as visualizações interativas geradas, reforçando a rastreabilidade entre os objetivos, perguntas e métricas adotadas.