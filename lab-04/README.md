# Projeto de Análise da Qualidade do Ar no Brasil com Dados da OpenAQ

## 1. Introdução

A poluição atmosférica é um dos maiores desafios ambientais contemporâneos, afetando diretamente a saúde pública, o bem-estar urbano e a dinâmica climática. Entre os poluentes mais monitorados encontram-se PM2.5, PM10, NO₂, SO₂, CO e O₃, todos associados a doenças respiratórias, cardiovasculares e ao aumento da mortalidade. A Organização Mundial da Saúde (OMS) estabelece limites de exposição para esses poluentes, mas diversos estudos indicam que grandes centros urbanos frequentemente ultrapassam tais recomendações.

Este trabalho investiga a qualidade do ar em cidades brasileiras com mais de 500 mil habitantes (definição do IBGE), utilizando exclusivamente dados abertos da plataforma **OpenAQ**, que consolida medições de estações oficiais e institucionais no mundo todo. O objetivo principal é construir uma base analítica e visual (dashboard BI) que permita identificar padrões espaciais, tendências temporais e excedências em relação às diretrizes da OMS.

O projeto segue o modelo **GQM (Goal–Question–Metric)** para garantir coerência entre coleta, métricas e análise.

---

## 2. GQM — Goal, Question, Metric

### **Goal (Objetivo Geral)**  
Investigar padrões espaciais e temporais da qualidade do ar em grandes cidades brasileiras, identificando excedências dos limites da OMS e estruturando esses dados em um dashboard de análise.

### **Questions (Questões de Pesquisa)**

1. **RQ1 – Variação Espacial**  
   Quais cidades apresentam os maiores valores médios de concentração de poluentes atmosféricos?

2. **RQ2 – Padrões Temporais e Sazonais**  
   Há variações significativas nas concentrações dos poluentes ao longo dos meses e anos disponíveis?

3. **RQ3 – Excedência dos Limites da OMS**  
   Qual o percentual de meses em que os poluentes ultrapassam as diretrizes da OMS em cada cidade?

### **Metrics (Métricas Associadas)**

- Média mensal e anual por poluente e por cidade.  
- Percentual de meses acima do limite da OMS.  
- Número de sensores disponíveis por cidade.  
- Período coberto pelas coletas (datetimeFrom, datetimeTo).  
- PercentCoverage para análise da qualidade e continuidade das séries.

---

## 3. Metodologia e Descrição da Base de Dados

A metodologia foi dividida em quatro etapas principais, todas automatizadas em Python.

---

### **3.1 Etapa 1 – Coleta de Dados (OpenAQ API)**

A coleta é feita via API pública **OpenAQ v3**, utilizando os seguintes endpoints:

- **/v3/locations**  
  Identifica sensores próximos às cidades-alvo utilizando busca geoespacial por raio (12 km em torno do centro urbano).

- **/v3/sensors/{sensor_id}/days/monthly**  
  Obtém médias mensais de todos os poluentes monitorados pelo sensor.

- **/v3/sensors/{sensor_id}/days/yearly**  
  Obtém agregações anuais para análises de tendência.

A API não oferece filtragem direta por nome de cidade, portanto utilizou-se um raio geoespacial aplicado às 35 cidades selecionadas (≥ 500 mil habitantes).

---

### **3.2 Etapa 2 – Processamento e Limpeza**

As etapas principais do pipeline foram:

1. Consulta das cidades e sensores identificados via bounding radius.  
2. Remoção de duplicatas de sensores compartilhados em áreas metropolitanas.  
3. Coleta de dados mensais e anuais para todos os sensores.  
4. Consolidação das informações em arquivos CSV:

   - `openaq_brazil_sensors.csv`  
   - `openaq_brazil_monthly.csv`  
   - `openaq_brazil_yearly.csv`  
   - `percentual_excedencia_por_cidade.csv`  
   - `info_sensores_por_cidade.csv`

As bibliotecas utilizadas incluem `requests`, `pandas`, `dotenv` e `time`.

---

### **3.3 Etapa 3 – Cálculo de Métricas (GQM)**

A partir dos CSVs brutos, o script realiza:

- agregação por cidade e poluente (média mensal e anual);
- cálculo de excedência comparando valores mensais aos limites da OMS;
- agrupamento por sensores da mesma cidade;
- identificação do período de coleta e qualidade das séries;
- criação de rankings por poluente e por cidade.

O CSV `percentual_excedencia_por_cidade.csv` sintetiza o RQ3.

---

### **3.4 Etapa 4 – Visualização e Dashboard BI**

Todos os CSVs são importados para o **Power BI**, onde foram construídas:

- páginas de variação espacial (mapas e rankings);
- páginas de séries temporais mensais e anuais;
- página dedicada às excedências da OMS;
- análises complementares (cobertura de sensores, lacunas temporais etc.).

A visualização final permite responder diretamente às três perguntas de pesquisa.

---

## 4. Arquivos Gerados

- `openaq_brazil_sensors.csv` – Lista de sensores por cidade.  
- `openaq_brazil_monthly.csv` – Dados mensais agregados por sensor.  
- `openaq_brazil_yearly.csv` – Dados anuais agregados por sensor.  
- `percentual_excedencia_por_cidade.csv` – Percentual de excedência dos limites OMS.  
- `info_sensores_por_cidade.csv` – Resumo de sensores, cobertura e período de coleta por cidade.

