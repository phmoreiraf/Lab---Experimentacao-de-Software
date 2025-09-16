#!/usr/bin/env python
import os, pandas as pd

CK_PATH = "data/metrics_merged.csv"
PROC_PATH = "data/repo_process_metrics.csv"
OUT = "data/summary_per_repo.csv"

TARGETS = ["cbo","dit","lcom","loc","loccomment","wmc","fanin","fanout"]

def main():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CK_PATH):
        raise SystemExit("Rodar merge antes (data/metrics_merged.csv).")
    if not os.path.exists(PROC_PATH):
        raise SystemExit("Rodar process antes (data/repo_process_metrics.csv).")

    ck = pd.read_csv(CK_PATH)
    proc = pd.read_csv(PROC_PATH)

    ck.columns = [c.lower() for c in ck.columns]
    present = [t for t in TARGETS if t in ck.columns]

    if not present:
        raise SystemExit("Nenhuma métrica alvo encontrada no CK unificado.")

    grp = ck.groupby("repo_id")[present].agg(["mean","median","std"])
    grp.columns = [f"{a}_{b}" for a,b in grp.columns]
    grp.reset_index(inplace=True)

    merged = grp.merge(proc, on="repo_id", how="left")
    merged.to_csv(OUT, index=False)
    print(f"[OK] {OUT} ({merged.shape[0]} repositórios)")

if __name__ == "__main__":
    main()
