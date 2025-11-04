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

A base de dados utilizada é proveniente da API pública OpenAQ v2, que fornece medições de qualidade do ar em formato JSON, coletadas por redes de monitoramento de diferentes países.
No contexto brasileiro, foram selecionadas as 27 capitais estaduais (lista armazenada em gh_api.py), e os parâmetros PM2.5 e PM10 foram definidos como variáveis principais.

O script realiza chamadas automáticas à API, respeitando limites de requisição e coletando os seguintes campos:

- city, uf, parameter, value, unit;
- date.utc, date.local;
- coordinates.latitude, coordinates.longitude;
- location (nome da estação).

Esses registros são salvos em CSV bruto (data/raw/openaq_brazil_capitals.csv), servindo como insumo para as etapas seguintes.

**3.2 Etapa 2 - Processamento e Limpeza**

O processamento ocorre no módulo dataset.py, que realiza:

- Conversão de data/hora para o formato local;
- Remoção de valores ausentes, duplicados ou negativos;
- Criação de novas colunas de data (year, month, day, dow, hour);
- Agregação diária por cidade e parâmetro, com cálculo das estatísticas:
    - Média diária (mean_value);
    - Valor máximo diário (max_value);
    - Número de medições (n_measurements).

Os resultados são exportados para data/processed/daily_city_parameter.csv, e uma tabela auxiliar dim_city.csv armazena latitude e longitude médias por cidade.
Essas duas tabelas são fundamentais para a extração das métricas do GQM, especialmente para Q1 e Q2.

**3.3 Etapa 3 - Consolidação de Métricas (GQM)**

Para atender às questões definidas no GQM, o pipeline será expandido para:

1. **Métricas espaciais (Q1):**
Cálculo de médias e desvios padrão por cidade e parâmetro.

2. **Métricas temporais (Q2):**
Agregações por mês, dia da semana e hora.

3. **Métricas de excedência (Q3):**
Percentual de dias acima dos limites definidos.

Essas métricas serão gravadas em novas tabelas auxiliares, como:

- agg_monthly_trends.csv - médias mensais por cidade e parâmetro;
- agg_hourly_patterns.csv - médias horárias para análise de sazonalidade diária;
- agg_exceedance.csv - percentuais de dias acima dos limites OMS.

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