import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# ---------------- Paths ----------------
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
PROC_DIR = os.path.join(DATA_DIR, "processed")
CHARTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "charts"))
REPORT_PATH = os.path.join(DATA_DIR, "metrics_report.md")

NUM_METRICS = [
    "size_files","size_additions","size_deletions",
    "analysis_hours","desc_len_chars",
    "interactions_participants","interactions_comments"
]

# ---------------- Utility functions ----------------

def _load_dataset(path: str = None) -> pd.DataFrame:
    if path is None:
        path = os.path.join(PROC_DIR, "dataset_prs.csv")
    df = pd.read_csv(path, parse_dates=["createdAt","endTime"])
    return df

def _ensure_dirs():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    for sub in ["hist","box","violin","scatter","corr", "bar"]:
        if sub in ["box","violin", "bar"]:
            for sub2 in ["status","reviews"]:
                os.makedirs(os.path.join(CHARTS_DIR, sub, sub2), exist_ok=True)
        os.makedirs(os.path.join(CHARTS_DIR, sub), exist_ok=True)

def _write(msg: str, header=False):
    """Escreve mensagens no relatório Markdown"""
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        if header:
            f.write(f"\n## {msg}\n")
        else:
            f.write(msg + "\n")
    print(msg)

def _clean_outliers(df: pd.DataFrame, lower_q=0.02, upper_q=0.98) -> pd.DataFrame:
    """Remove outliers com base em quantis (menos agressivo que o IQR)"""
    for col in NUM_METRICS + ["reviews_count"]:
        if col in df.columns:
            q_low = df[col].quantile(lower_q)
            q_hi = df[col].quantile(upper_q)
            df = df[(df[col] >= q_low) & (df[col] <= q_hi)]
    return df

def _spearman_series(df: pd.DataFrame, y: str) -> pd.DataFrame:
    """Correlação de Spearman entre cada métrica e a variável y"""
    rows = []
    for x in NUM_METRICS:
        s = df[[x, y]].dropna()
        if len(s) < 5:
            continue
        rho, p = stats.spearmanr(s[x], s[y])
        rows.append({
            "metric": x,
            "rho": rho,
            "p": p,
            "significant": "YES" if p < 0.05 else "NO"
        })
    return pd.DataFrame(rows).sort_values("rho", ascending=False)

def charts_basic(df: pd.DataFrame):
    """Gera gráficos exploratórios básicos"""
    _ensure_dirs()

    # Histograms
    for m in NUM_METRICS + ["reviews_count"]:
        plt.figure(figsize=(7,4))
        plt.hist(df[m].dropna(), bins=40)
        plt.title(f"Histogram - {m}")
        plt.xlabel(m); plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "hist", f"hist_{m}.png"))
        plt.close()

    # Heatmap de correlações
    corr_spear = df[NUM_METRICS + ["reviews_count","final_status_bin"]].corr(method="spearman")
    plt.figure(figsize=(8,7))
    sns.heatmap(corr_spear, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Spearman Correlations")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "corr", "heatmap_spearman.png"))
    plt.close()

    # Boxplots por status
    for m in NUM_METRICS:
        plt.figure(figsize=(6,4))
        sns.boxplot(x="final_status_bin", y=m, data=df, showfliers=False)
        plt.title(f"{m} by PR status")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "box", "status", f"box_{m}_by_status.png"))
        plt.close()

        sns.violinplot(x="final_status_bin", y=m, data=df, cut=0, inner="quartile") 
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "violin", "status", f"violin_{m}_by_status.png")) 
        plt.close()

    # Boxplots por revisões
    for m in NUM_METRICS:
        plt.figure(figsize=(6,4))
        sns.boxplot(x="reviews_count", y=m, data=df, showfliers=False)
        plt.title(f"{m} by PR status")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "box", "reviews", f"box_{m}_by_reviews.png"))
        plt.close()

        sns.violinplot(x="reviews_count", y=m, data=df, cut=0, inner="quartile") 
        plt.tight_layout() 
        plt.savefig(os.path.join(CHARTS_DIR, "violin", "reviews", f"violin_{m}_by_reviews.png")) 
        plt.close()

    # Scatter com número de revisões
    for m in NUM_METRICS:
        plt.figure(figsize=(6,4))
        plt.scatter(df[m], df["reviews_count"], alpha=0.5)
        plt.xlabel(m); plt.ylabel("reviews_count")
        plt.title(f"{m} vs reviews_count")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "scatter", f"scatter_{m}_vs_reviews.png"))
        plt.close()

    # Barras médias por status
    for m in NUM_METRICS:
        plt.figure(figsize=(6,4))
        mean = df.groupby("final_status_bin")[m].mean().reset_index()
        sns.barplot(x="final_status_bin", y=m, data=mean, palette="viridis")
        plt.title(f"Mean {m} by PR status")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "bar", "status", f"bar_mean_{m}_by_status.png"))
        plt.close()

    # Barras por revisões
    for m in NUM_METRICS:
        plt.figure(figsize=(6,4))
        mean = df.groupby("reviews_count")[m].mean().reset_index()
        sns.barplot(x="reviews_count", y=m, data=mean, palette="viridis")
        plt.title(f"Mean {m} by reviews_count")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "bar", "reviews", f"bar_mean_{m}_by_reviews.png"))
        plt.close()

    


# ---------------- Análises ----------------

def rq_status_analysis(df: pd.DataFrame):
    """Análise das RQs 1–4: relação das métricas com o status final (MERGED vs CLOSED)"""
    _write("Análise RQ A – Feedback final das revisões", header=True)

    # Correlações (Spearman)
    s = _spearman_series(df, "final_status_bin")
    _write("\n### Correlação de Spearman com 'final_status_bin' (MERGED=1):")
    _write(s.to_markdown(index=False))

    # Teste de Mann–Whitney
    _write("\n### Teste de Mann–Whitney (diferença entre MERGED e CLOSED):")
    rows = []
    for m in NUM_METRICS:
        merged = df[df.final_status == "MERGED"][m].dropna()
        closed = df[df.final_status == "CLOSED"][m].dropna()
        if len(merged) < 5 or len(closed) < 5:
            continue
        stat, p = stats.mannwhitneyu(merged, closed, alternative="two-sided")
        rows.append({
            "metric": m, 
            "U": stat,
            "p": p,
            "significant": "YES" if p < 0.05 else "NO"
        })
    _write(pd.DataFrame(rows).to_markdown(index=False))

def rq_reviews_analysis(df: pd.DataFrame):
    """Análise das RQs 5–8: relação das métricas com o número de revisões"""
    _write("Análise RQ B – Número de revisões realizadas", header=True)
    s = _spearman_series(df, "reviews_count")
    _write("\n### Correlação de Spearman com 'reviews_count':")
    _write(s.to_markdown(index=False))

def median_summary(df: pd.DataFrame):
    """Resumo de medias das métricas"""
    _write("Resumo das medias das Métricas", header=True)
    desc = df[NUM_METRICS + ["reviews_count"]].describe().T
    desc = desc.rename(
        columns={
            "count": "N",
            "mean": "Média",
            "std": "Desvio Padrão",
            "min": "Mínimo",
            "25%": "Q1",
            "50%": "Mediana",
            "75%": "Q3",
            "max": "Máximo"
        }
    )

    desc.index.name = "Métrica"
    desc.reset_index(inplace=True)
    _write(desc.to_markdown(index=False))

# ---------------- Runner ----------------

# --------- Relatório narrativo Markdown (para entrega) ---------

def generate_markdown_report(df: pd.DataFrame, path=os.path.join(DATA_DIR, "report_lab03.md")):
    med = df[NUM_METRICS + ["reviews_count"]].median().to_frame("median")
    # Correlações principais (Spearman)
    s_status = df[NUM_METRICS + ["final_status_bin"]].corr(method="spearman")["final_status_bin"].drop("final_status_bin")
    s_reviews = df[NUM_METRICS + ["reviews_count"]].corr(method="spearman")["reviews_count"].drop("reviews_count")

    lines = []
    lines.append("# LAB-03 – Relatório Final\n")
    lines.append("## 1. Introdução e hipóteses\n")
    lines.append("- Hipótese A: PRs maiores e mais longos tendem a **reduzir** a chance de *merge*.\n- Hipótese B: PRs com mais interações tendem a **ter mais revisões**.\n")
    lines.append("## 2. Metodologia\n")
    lines.append("- 200 repositórios mais populares (≥100 PRs MERGED+CLOSED)\n- PRs MERGED/CLOSED, ≥1 review, duração ≥1h\n- Métricas: tamanho (arquivos/adições/remoções), tempo, descrição, interações (participantes, comentários de *issue*, *review threads*)\n- Testes: Spearman (e Point-biserial/PEARSON para status), regressão logística; viz: box/violin, heatmaps, scatter.\n")
    lines.append("## 3. Resultados\n### 3.1 Medianas (todos os PRs)\n")
    lines.append(med.to_markdown())
    lines.append("\n### 3.2 Correlações (Spearman) com *status* (MERGED=1)\n")
    lines.append(s_status.sort_values(ascending=False).to_frame("rho").to_markdown())
    lines.append("\n### 3.3 Correlações (Spearman) com `reviews_count`\n")
    lines.append(s_reviews.sort_values(ascending=False).to_frame("rho").to_markdown())
    lines.append("\n## 4. Discussão\n")
    lines.append("- Compare sinais/força com as hipóteses; discuta trade-offs de PRs grandes versus chances de *merge* e necessidade de revisões.\n- Limitações: amostragem enviesada por popularidade, linguagens diversas, *rate limits*, automações/bots, efeitos de processo por projeto.\n")
    lines.append("## 5. Conclusões\n")
    lines.append("- Principais associações encontradas e implicações práticas para submissão de PRs.\n")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def run_all(dataset_path: str = None):
    if os.path.exists(REPORT_PATH):
        os.remove(REPORT_PATH)
    df = _load_dataset(dataset_path)
    print(f"[i] Dataset carregado com {len(df)} PRs.")
    df = _clean_outliers(df)
    print(f"[i] Dataset após remoção de outliers: {len(df)} PRs.")
    print(f"Numero de prs closed: {len(df[df.final_status=='CLOSED'])}")
    print(f"Numero de prs merged: {len(df[df.final_status=='MERGED'])}")
    charts_basic(df)
    median_summary(df)
    rq_status_analysis(df)
    rq_reviews_analysis(df)
    _write("\n---\nAnálise concluída. Resultados salvos em 'data/metrics_report.md' e gráficos em 'charts/'.")
