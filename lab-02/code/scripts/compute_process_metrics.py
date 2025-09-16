#!/usr/bin/env python
import os
import pandas as pd
from datetime import datetime, timezone

INP = "data/repos.csv"
OUT = "data/repo_process_metrics.csv"

def iso_to_dt(s):
    s = str(s)
    return datetime.fromisoformat(s.replace("Z","+00:00"))

def years_between(a, b):
    return (b - a).days / 365.25

def main():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(INP):
        raise SystemExit(f"{INP} não encontrado. Rode 'make fetch' antes.")

    df = pd.read_csv(INP)
    # tenta mapear nomes das colunas que vêm do GraphQL
    # nameWithOwner, createdAt, updatedAt, releases.totalCount, pullRequests.totalCount etc.
    # No seu salvamento atual o header é mais simples (ver csv_controller.py)
    # Vamos assumir colunas: nameWithOwner, createdAt, updatedAt, releases, mergedPRs, totalIssues, closedIssues
    required = ["nameWithOwner","createdAt","updatedAt","releases"]
    for r in required:
        if r not in df.columns:
            raise SystemExit(f"Coluna '{r}' ausente em {INP}. Verifique csv_controller.py.")

    now = datetime.now(timezone.utc)
    rows = []
    for _, r in df.iterrows():
        full = r["nameWithOwner"]
        created = iso_to_dt(r["createdAt"])
        idade = years_between(created, now)
        releases = int(r.get("releases", 0))
        # stars não veio direto no CSV GraphQL atual; podemos coletar numa versão futura.
        # Para cumprir o LAB02, seguiremos com as demais e LOC via CK.
        rows.append({"repo_id": full.replace("/","__"), "full_name": full,
                     "idade_anos": idade, "releases": releases})

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"[OK] {OUT}")

if __name__ == "__main__":
    main()
