.PHONY: install run analyze fetch process bi report all clean

install:
	python -m pip install -r requirements.txt

# Executa o menu interativo
run:
	python main.py

# Pipeline completo (sem menu)
all: fetch process bi report

# 1) Coleta (dados públicos OpenAQ)
fetch:
	python - << 'PY'
import dataset
dataset.fetch_latest_measurements(days=180)
print("[✓] Coleta concluída em data/raw/")
PY

# 2) Processamento (tabelas diárias + dimensão cidade)
process:
	python - << 'PY'
import dataset
dataset.build_daily_tables()
print("[✓] Processamento concluído em data/processed/")
PY

# 3) Exporta fato/dimensões/aggregates p/ BI
bi:
	python - << 'PY'
import analysis_rqs
analysis_rqs.build_bi_outputs()
print("[✓] Artefatos BI gerados em data/bi/")
PY

# 4) Gera relatório (i–iv)
report:
	python - << 'PY'
import analysis_rqs
analysis_rqs.generate_report_md()
print("[✓] Relatório gerado em docs/report_alt.md")
PY

# Atalho pra gerar BI + relatório
analyze: bi report

clean:
	python - << 'PY'
import os, shutil
for p in ["data/raw","data/processed","data/bi"]:
    os.makedirs(p, exist_ok=True)
    for f in os.listdir(p):
        fp = os.path.join(p,f)
        if os.path.isfile(fp): os.remove(fp)
docs = "docs/report_alt.md"
if os.path.isfile(docs): os.remove(docs)
print("[✓] Limpeza concluída")
PY
