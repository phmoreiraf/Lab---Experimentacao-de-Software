# LAB-03 – Caracterizando a atividade de *code review* no GitHub

**Objetivo**: coletar *Pull Requests* (PRs) dos **200 repositórios mais populares** (por estrelas) que possuam **≥ 100 PRs MERGED + CLOSED**, filtrar PRs que  
1) têm **pelo menos 1 revisão**, e  
2) levaram **≥ 1 hora** do `createdAt` até `mergedAt`/`closedAt`,  
e então **responder às RQs** via correlações e visualizações sobre os PRs (conjunto único – não por repositório).

## Estrutura
lab-03/
├─ code/
│ ├─ .env.example
│ ├─ gh_api.py
│ ├─ dataset.py
│ ├─ analysis_rqs.py
│ └─ main.py
├─ data/
│ ├─ raw/
│ └─ processed/
├─ charts/
├─ Slides/
├─ requirements.txt
├─ Makefile
└─ README.md

## Instalação
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
