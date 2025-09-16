
---

# Makefile (novo)

```makefile
# Tamanho da amostra (p/ coleta GraphQL e CK). Padrão 1000
TOP ?= 1000

.PHONY: all fetch measure merge process summarize analyze report clean

all: fetch measure merge process summarize analyze report

# Coleta top-N repos Java (GraphQL) e salva data/repos.csv
fetch:
	. .venv/bin/activate && python scripts/fetch_repos.py --top $(TOP) --out data/repos.csv

# Clona repos listados em data/repos.csv e roda CK
measure:
	bash scripts/clone_and_measure.sh data/repos.csv

# Unifica saídas do CK em data/metrics_merged.csv
merge:
	. .venv/bin/activate && python scripts/merge_ck_outputs.py

# Deriva métricas de processo (stars, idade, releases)
process:
	. .venv/bin/activate && python scripts/compute_process_metrics.py

# Sumariza por repositório (médias/medianas/desvios CK) e junta a processo
summarize:
	. .venv/bin/activate && python scripts/summarize_per_repo.py

# RQ1–RQ4: correlações, CSV por par (X,Y) e figuras
analyze:
	. .venv/bin/activate && python scripts/analyze_rqs.py --export

# Relatório final (markdown)
report:
	. .venv/bin/activate && python scripts/build_report.py

clean:
	rm -rf data/metrics_raw/* data/metrics_merged.csv data/repo_process_metrics.csv \
           data/summary_per_repo.csv data/figures/* data/exports/* reports/report.md
