#!/usr/bin/env python
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

INP = "data/summary_per_repo.csv"
FIGDIR = "data/figures"
EXPORT_DIR = "data/exports"

QUALITY = ["cbo_mean","cbo_median","dit_mean","dit_median","lcom_mean","lcom_median"]

def ensure(d): os.makedirs(d, exist_ok=True)

def corr_table(x, ys, df):
    rows = []
    for y in ys:
        if x not in df.columns or y not in df.columns:
            rows.append((y, np.nan, np.nan, np.nan, np.nan, 0))
            continue
        a = df[x].values; b = df[y].values
        m = ~np.isnan(a) & ~np.isnan(b)
        if m.sum() < 3:
            rows.append((y, np.nan, np.nan, np.nan, np.nan, m.sum()))
            continue
        pr, pp = pearsonr(a[m], b[m])
        sr, sp = spearmanr(a[m], b[m])
        rows.append((y, pr, pp, sr, sp, m.sum()))
    return pd.DataFrame(rows, columns=["metric","pearson_r","pearson_p","spearman_rho","spearman_p","n"])

def scatter(df, x, y, title, path):
    plt.figure()
    plt.scatter(df[x], df[y], s=10, alpha=0.6)
    plt.xlabel(x); plt.ylabel(y); plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def export_pair(df, x, y):
    if all(c in df.columns for c in ["repo_id", x, y]):
        out = os.path.join(EXPORT_DIR, f"{x}_vs_{y}.csv")
        df[["repo_id", x, y]].dropna().to_csv(out, index=False)

def main():
    ensure(FIGDIR); ensure(EXPORT_DIR)
    if not os.path.exists(INP):
        raise SystemExit(f"{INP} ausente. Rode summarize antes.")
    df = pd.read_csv(INP)

    # RQ1 (popularidade) – requer stars; se não houver ainda, gera vazio
    if "stars" in df.columns:
        rq1 = corr_table("stars", QUALITY, df)
        rq1.to_csv("data/rq1_correlations.csv", index=False)
    else:
        pd.DataFrame(columns=["metric","pearson_r","pearson_p","spearman_rho","spearman_p","n"]).to_csv("data/rq1_correlations.csv", index=False)

    # RQ2 (maturidade)
    rq2 = corr_table("idade_anos", QUALITY, df); rq2.to_csv("data/rq2_correlations.csv", index=False)

    # RQ3 (atividade)
    rq3 = corr_table("releases", QUALITY, df); rq3.to_csv("data/rq3_correlations.csv", index=False)

    # RQ4 (tamanho – LOC médio)
    if "loc_mean" in df.columns:
        rq4 = corr_table("loc_mean", QUALITY, df); rq4.to_csv("data/rq4_loc_correlations.csv", index=False)
    else:
        pd.DataFrame(columns=["metric","pearson_r","pearson_p","spearman_rho","spearman_p","n"]).to_csv("data/rq4_loc_correlations.csv", index=False)

    # SEMPRE exporta CSV por par (X,Y) e gera os gráficos
    pairs = []
    if "stars" in df.columns: pairs += [("stars", y) for y in QUALITY]
    pairs += [("idade_anos", y) for y in QUALITY]
    pairs += [("releases", y) for y in QUALITY]
    if "loc_mean" in df.columns: pairs += [("loc_mean", y) for y in QUALITY]

    for x,y in pairs:
        export_pair(df, x, y)
        scatter(df, x, y, f"{x} vs {y}", os.path.join(FIGDIR, f"{x}_vs_{y}.png"))

    # Heatmap (se houver colunas suficientes)
    cols = [c for c in ["stars","idade_anos","releases","loc_mean"] if c in df.columns] + [c for c in QUALITY if c in df.columns]
    if len(cols) >= 3:
        plt.figure()
        corr = df[cols].corr(method="pearson")
        im = plt.imshow(corr, interpolation="nearest")
        plt.colorbar(im, fraction=0.046, pad=0.04)
        plt.xticks(range(len(cols)), cols, rotation=45, ha="right")
        plt.yticks(range(len(cols)), cols)
        plt.title("Correlação (Pearson) — Processo vs Qualidade")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGDIR, "heatmap_process_quality.png"), dpi=150)
        plt.close()

    print("[OK] RQ1–RQ4: tabelas em data/rq*.csv; pares em data/exports/; figuras em data/figures/.")

if __name__ == "__main__":
    main()
