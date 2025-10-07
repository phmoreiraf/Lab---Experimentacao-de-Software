# LAB-03 – Caracterizando a atividade de *code review* no GitHub

**Objetivo**: coletar Pull Requests (PRs) dos **200 repositórios mais populares** (por estrelas) que possuam **≥ 100 PRs MERGED + CLOSED**; filtrar PRs que  
1) têm **pelo menos 1 revisão**, e  
2) levaram **≥ 1 hora** do `createdAt` até `mergedAt`/`closedAt`,  
e então **responder às RQs** com correlações (Spearman/Pearson), regressão logística e visualizações. O conjunto analisado é **o total de PRs** (não por repositório).

## Estrutura

lab-03/
├─ code/
│ ├─ .env.example
│ ├─ gh_api.py
│ ├─ dataset.py
│ ├─ analysis_rqs.py
│ ├─ requirements.txt
│ ├─ Makefile
│ └─ main.py
├─ data/
│ ├─ raw/
│ └─ processed/
├─ charts/
├─ Slides/
└─ README.md

## Instalação
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp code/.env.example code/.env   # e edite GITHUB_TOKEN

python -m code.main fetch-repos --n 200 --min-prs 100
python -m code.main fetch-prs --max-per-repo 500
python -m code.main analyze
# Saídas:
# - charts/* (figuras)
# - data/metrics_report.txt (estatísticas)
# - data/report_lab03.md (relatório narrativo)

Métricas por PR

Tamanho: size_files, size_additions, size_deletions

Tempo: analysis_hours

Descrição: desc_len_chars

Interações: interactions_participants, interactions_comments_issue, interactions_review_threads, interactions_comments (= soma)

Outras: reviews_count, final_status, final_status_bin

RQs

Dimensão A – Status (MERGED vs CLOSED)

Tamanho ↔ Status

Tempo ↔ Status

Descrição ↔ Status

Interações ↔ Status

Dimensão B – Número de revisões

Tamanho ↔ reviews_count

Tempo ↔ reviews_count

Descrição ↔ reviews_count

Interações ↔ reviews_count


---

# Slides/Lab3-Apresentacao.md
```markdown
# Slides (LAB-03)

## 1. Contexto
- Caracterização de code review via PRs (GitHub GraphQL)

## 2. Metodologia
- Top 200 repositórios com ≥100 PRs MERGED+CLOSED
- PRs filtrados: ≥1 review e duração ≥1h
- Métricas: tamanho, tempo, descrição, interações (issue comments, review threads), status, #reviews

## 3. RQs
- A: métricas ↔ *status* (MERGED vs CLOSED)
- B: métricas ↔ *reviews_count*

## 4. Resultados
- Medianas gerais e correlações (Spearman/Pearson)
- Regressão logística (status ~ métricas)
- Gráficos: box/violin, heatmaps, scatter, hist

## 5. Conclusões
- Principais associações e implicações
- Limitações e trabalhos futuros
