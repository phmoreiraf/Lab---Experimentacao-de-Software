.PHONY: install run analyze fetch process bi report all clean

install:
	python -m pip install -r requirements.txt

run:
	python main.py

all: fetch process bi report

# 1) Coleta (agora 365 dias e cidades >500k por padrão)
fetch:
	python - << 'PY'
import dataset
dataset.fetch_latest_measurements(days=365, city_set="500K")
print("[✓] Coleta concluída em data/raw/")
PY

process:
	python - << 'PY'
import dataset
dataset.build_daily_tables()
print("[✓] Processamento concluído em data/processed/")
PY

bi:
	python - << 'PY'
import analysis_rqs
analysis_rqs.build_bi_outputs()
print("[✓] Artefatos BI gerados em data/bi/")
PY

report:
	python - << 'PY'
import analysis_rqs
analysis_rqs.generate_report_md()
print("[✓] Relatório gerado em docs/report_alt.md")
PY

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
plots = "docs/plots"
if os.path.isdir(plots): 
    import shutil; shutil.rmtree(plots, ignore_errors=True)
print("[✓] Limpeza concluída")
PY
