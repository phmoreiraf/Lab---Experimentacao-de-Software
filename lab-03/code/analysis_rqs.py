import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
PROC_DIR = os.path.join(DATA_DIR, "processed")
CHARTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "charts"))
REPORT_PATH = os.path.join(DATA_DIR, "metrics_report.txt")

NUM_METRICS = [
    "size_files","size_additions","size_deletions",
    "analysis_hours","desc_len_chars",
    "interactions_participants","interactions_comments"
]

def _load_dataset(path: str = None) -> pd.DataFrame:
    if path is None:
        path = os.path.join(PROC_DIR, "dataset_prs.csv")
    df = pd.read_csv(path, parse_dates=["createdAt","endTime"])
    return df

def _ensure_dirs():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    for sub in ["hist","box","violin","scatter","corr","bar"]:
        os.makedirs(os.path.join(CHARTS_DIR, sub), exist_ok=True)

def _write(msg: str):
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def _spearman_series(df: pd.DataFrame, y: str) -> pd.DataFrame:
    rows = []
    for x in NUM_METRICS:
        s = df[[x, y]].dropna()
        if len(s) < 5: 
            rows.append({"metric": x, "rho": np.nan, "p": np.nan})
            continue
        rho, p = stats.spearmanr(s[x], s[y])
        rows.append({"metric": x, "rho": rho, "p": p})
    return pd.DataFrame(rows).sort_values("rho", ascending=False)

def _pearson_series(df: pd.DataFrame, y: str) -> pd.DataFrame:
    rows = []
    for x in NUM_METRICS:
        s = df[[x, y]].dropna()
        if len(s) < 5:
            rows.append({"metric": x, "r": np.nan, "p": np.nan})
            continue
        r, p = stats.pearsonr(s[x], s[y])
        rows.append({"metric": x, "r": r, "p": p})
    return pd.DataFrame(rows).sort_values("r", ascending=False)

def _logit(df: pd.DataFrame, y: str, X_cols):
    s = df[X_cols + [y]].dropna()
    if s.empty: 
        return None
    X = sm.add_constant(s[X_cols])
    yv = s[y]
    try:
        model = sm.Logit(yv, X).fit(disp=False, maxiter=200)
    except Exception:
        return None
    return model

def _median_summary(df: pd.DataFrame) -> pd.DataFrame:
    med = df[NUM_METRICS + ["reviews_count"]].median().to_frame(name="median").T
    return med

def charts_basic(df: pd.DataFrame):
    _ensure_dirs()
    # Histograms
    for m in NUM_METRICS + ["reviews_count"]:
        plt.figure(figsize=(7,4))
        plt.hist(df[m].dropna(), bins=40)
        plt.title(f"Histogram - {m}")
        plt.xlabel(m); plt.ylabel("Freq")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "hist", f"hist_{m}.png")); plt.close()

    # Correlation heatmaps
    corr_pearson = df[NUM_METRICS + ["reviews_count","final_status_bin"]].corr(method="pearson")
    corr_spear = df[NUM_METRICS + ["reviews_count","final_status_bin"]].corr(method="spearman")

    plt.figure(figsize=(8,7))
    sns.heatmap(corr_pearson, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Pearson Correlations")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "corr", "heatmap_pearson.png")); plt.close()

    plt.figure(figsize=(8,7))
    sns.heatmap(corr_spear, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Spearman Correlations")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "corr", "heatmap_spearman.png")); plt.close()

    # Box/violin by final status
    for m in NUM_METRICS:
        plt.figure(figsize=(6,4))
        sns.boxplot(x="final_status", y=m, data=df, showfliers=False)
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "box", f"box_{m}_by_status.png")); plt.close()

        plt.figure(figsize=(6,4))
        sns.violinplot(x="final_status", y=m, data=df, cut=0, inner="quartile")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "violin", f"violin_{m}_by_status.png")); plt.close()

    # Scatter vs #reviews
    for m in NUM_METRICS:
        plt.figure(figsize=(6,4))
        plt.scatter(df[m], df["reviews_count"], alpha=0.5)
        plt.xlabel(m); plt.ylabel("reviews_count")
        plt.title(f"{m} vs reviews_count")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, "scatter", f"scatter_{m}_vs_reviews.png")); plt.close()

# ---------------- RQs ----------------

def rq_status_correlations(df: pd.DataFrame):
    _write("=== RQ A (feedback final / status MERGED vs CLOSED) ===")
    # Spearman with binary final_status_bin
    s = _spearman_series(df, "final_status_bin")
    _write("\nSpearman (rho, p) with final_status_bin=1 for MERGED:")
    _write(s.to_string(index=False))

    # Also point-biserial (equivalent to Pearson with binary y)
    p = _pearson_series(df, "final_status_bin")
    _write("\nPoint-biserial (Pearson) with final_status_bin:")
    _write(p.to_string(index=False))

    # Logistic regression as robustness
    model = _logit(df, "final_status_bin", NUM_METRICS)
    if model:
        _write("\nLogistic regression (status_bin ~ metrics) summary:")
        _write(str(model.summary()))
    else:
        _write("\n[!] Logistic regression didn't converge or no data.")

def rq_reviews_correlations(df: pd.DataFrame):
    _write("\n=== RQ B (número de revisões) ===")
    # Spearman with reviews_count
    rows = []
    for x in NUM_METRICS:
        s = df[[x, "reviews_count"]].dropna()
        if len(s) < 5:
            rows.append({"metric": x, "rho": np.nan, "p": np.nan})
            continue
        rho, p = stats.spearmanr(s[x], s["reviews_count"])
        rows.append({"metric": x, "rho": rho, "p": p})
    res = pd.DataFrame(rows).sort_values("rho", ascending=False)
    _write("\nSpearman (rho, p) with reviews_count:")
    _write(res.to_string(index=False))

def median_summary(df: pd.DataFrame):
    _write("\n=== Median summary of all PRs (not grouped by repository) ===")
    _write(_median_summary(df).to_string(index=False))

def run_all(dataset_path: str = None):
    if os.path.exists(REPORT_PATH):
        os.remove(REPORT_PATH)
    df = _load_dataset(dataset_path)
    # Optionally remove extreme outliers to stabilize viz
    for col in NUM_METRICS + ["reviews_count"]:
        if col in df.columns:
            q_hi = df[col].quantile(0.99)
            df = df[df[col] <= q_hi]
    charts_basic(df)
    median_summary(df)
    rq_status_correlations(df)
    rq_reviews_correlations(df)
    _write("\n[done] Charts saved in charts/ and report at data/metrics_report.txt")
