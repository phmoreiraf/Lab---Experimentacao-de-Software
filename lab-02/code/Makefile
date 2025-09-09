
---

## `Makefile` (sem Docker)

```makefile
# Controla o tamanho da amostra (default 1000)
TOP ?= 1000

.PHONY: all fetch measure merge process summarize analyze report pdf clean help exports

all: fetch measure merge process summarize analyze report

fetch:
	. .venv/bin/activate && python scripts/fetch_repos.py --top $(TOP) --out data/repos.csv

measure:
	bash scripts/clone_and_measure.sh data/repos.csv

merge:
	. .venv/bin/activate && python scripts/merge_ck_outputs.py

process:
	. .venv/bin/activate && python scripts/compute_process_metrics.py

summarize:
	. .venv/bin/activate && python scripts/summarize_per_repo.py

# Gera correlações + figuras + CSVs finos por par (X,Y)
analyze:
	. .venv/bin/activate && python scripts/analyze_rqs.py --export

# Só exporta os CSVs por par (X,Y) — sem recomputar correlações
exports:
	. .venv/bin/activate && python scripts/analyze_rqs.py --export-only

report:
	. .venv/bin/activate && python scripts/build_report.py

pdf: reports/report.md
	@echo "[PDF] Gerando reports/report.pdf via pandoc..."
	pandoc reports/report.md \
	       --from=gfm \
	       --pdf-engine=xelatex \
	       -V mainfont="Latin Modern Roman" \
	       -V geometry:margin=2.5cm \
	       -o reports/report.pdf
	@echo "[OK] PDF em reports/report.pdf"

clean:
	rm -rf data/metrics_raw/* data/metrics_merged.csv data/repo_process_metrics.csv \
           data/summary_per_repo.csv data/figures/* data/exports/* reports/report.md reports/report.pdf

help:
	@echo "Alvos:"
	@echo "  TOP=100 make all   -> pipeline completa com top 100"
	@echo "  make analyze       -> RQ1–RQ4, gráficos e CSVs em data/exports/"
	@echo "  make pdf           -> gera reports/report.pdf"
