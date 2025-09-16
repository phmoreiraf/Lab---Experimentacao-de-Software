# analise.py
# -----------------------------------------------------------
# Análises exploratórias dos repositórios coletados via GraphQL.
# Mantém todos os gráficos existentes e substitui APENAS o ECDF de PRs
# por um heatmap 2D de densidade (mergedPRs vs stargazerCount ou releases).
# -----------------------------------------------------------

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# -----------------------------------------------------------
# Utils
# -----------------------------------------------------------
def _ensure_dir(d: str):
    os.makedirs(d, exist_ok=True)

def _savefig(path: str):
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def _as_numeric(df: pd.DataFrame, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def _plot_bar_counts(series: pd.Series, title: str, xlabel: str, ylabel: str, outpath: str, top: int = 20):
    plt.figure()
    series.value_counts().head(top).plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    _savefig(outpath)

def _plot_hist(series: pd.Series, title: str, xlabel: str, ylabel: str, outpath: str, bins: int = 40):
    plt.figure()
    series.dropna().plot(kind="hist", bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    _savefig(outpath)

def _plot_scatter(x: pd.Series, y: pd.Series, title: str, xlabel: str, ylabel: str, outpath: str):
    plt.figure()
    plt.scatter(x, y, s=10, alpha=0.6)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    _savefig(outpath)

def _plot_heatmap_2d(x: pd.Series, y: pd.Series, title: str, xlabel: str, ylabel: str, outpath: str, bins: int = 40):
    """
    Substituição do ECDF de PRs: gera um heatmap 2D de densidade (histograma conjunto).
    """
    # Máscara para alinhar índices e remover NaNs
    mask = (~pd.isna(x)) & (~pd.isna(y))
    x_vals = pd.to_numeric(x[mask], errors="coerce").dropna().values
    y_vals = pd.to_numeric(y[mask], errors="coerce").dropna().values
    if len(x_vals) < 3:
        # Muito pouco dado — evita figura "vazia"
        return

    H, xedges, yedges = np.histogram2d(x_vals, y_vals, bins=bins)
    H = H.T  # imshow espera [linhas=y, colunas=x]

    plt.figure()
    plt.imshow(
        H,
        interpolation="nearest",
        origin="lower",
        aspect="auto",
        extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
    )
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    _savefig(outpath)

# -----------------------------------------------------------
# Público
# -----------------------------------------------------------
def analisar_repositorios(csv_path: str, auto_save: bool = True, charts_dir: str = "charts"):
    """
    Lê o CSV de repositórios (GraphQL) e gera gráficos exploratórios.
    Mantém TODOS os gráficos existentes e substitui APENAS o ECDF de PRs por HEATMAP 2D:
      - Preferência: stargazerCount × mergedPRs
      - Fallback:    releases × mergedPRs
    """
    _ensure_dir(charts_dir)
    df = pd.read_csv(csv_path)

    # Campos esperados (ajuste se necessário)
    # nameWithOwner, stargazerCount, createdAt, updatedAt, primaryLanguage,
    # mergedPRs, releases, totalIssues, closedIssues
    numeric_cols = ["stargazerCount", "mergedPRs", "releases", "totalIssues", "closedIssues"]
    df = _as_numeric(df, numeric_cols)

    # -------------------------
    # Gráficos já existentes
    # -------------------------

    # Top linguagens
    if "primaryLanguage" in df.columns:
        _plot_bar_counts(
            df["primaryLanguage"],
            title="Top 20 linguagens primárias",
            xlabel="Linguagem",
            ylabel="Quantidade de repositórios",
            outpath=os.path.join(charts_dir, "top_linguagens.png"),
            top=20,
        )

    # Distribuições (hist)
    if "stargazerCount" in df.columns:
        _plot_hist(
            df["stargazerCount"],
            title="Distribuição de estrelas (stargazerCount)",
            xlabel="Estrelas",
            ylabel="Frequência",
            outpath=os.path.join(charts_dir, "dist_estrelas.png"),
            bins=40,
        )

    if "mergedPRs" in df.columns:
        _plot_hist(
            df["mergedPRs"],
            title="Distribuição de PRs mesclados (mergedPRs)",
            xlabel="PRs mesclados",
            ylabel="Frequência",
            outpath=os.path.join(charts_dir, "dist_mergedPRs.png"),
            bins=40,
        )

    if "releases" in df.columns:
        _plot_hist(
            df["releases"],
            title="Distribuição de releases",
            xlabel="Releases",
            ylabel="Frequência",
            outpath=os.path.join(charts_dir, "dist_releases.png"),
            bins=40,
        )

    # Issues totais vs fechadas (barras)
    if "totalIssues" in df.columns and "closedIssues" in df.columns:
        plt.figure()
        df[["totalIssues", "closedIssues"]].sum().plot(kind="bar")
        plt.title("Issues: totais vs fechadas (soma da amostra)")
        plt.xlabel("Tipo")
        plt.ylabel("Quantidade")
        _savefig(os.path.join(charts_dir, "issues_totais_vs_fechadas.png"))

    # Scatter exploratórios
    if "stargazerCount" in df.columns and "releases" in df.columns:
        _plot_scatter(
            df["stargazerCount"],
            df["releases"],
            title="Estrelas vs Releases (exploratório)",
            xlabel="Estrelas",
            ylabel="Releases",
            outpath=os.path.join(charts_dir, "estrelas_vs_releases.png"),
        )

    if "stargazerCount" in df.columns and "mergedPRs" in df.columns:
        _plot_scatter(
            df["stargazerCount"],
            df["mergedPRs"],
            title="Estrelas vs PRs mesclados (exploratório)",
            xlabel="Estrelas",
            ylabel="PRs mesclados",
            outpath=os.path.join(charts_dir, "estrelas_vs_mergedPRs.png"),
        )

    # -----------------------------------------------------------
    # SUBSTITUIÇÃO DO ECDF DE PRs -> HEATMAP 2D (apenas este bloco muda)
    # -----------------------------------------------------------
    if "stargazerCount" in df.columns and "mergedPRs" in df.columns:
        _plot_heatmap_2d(
            df["stargazerCount"],
            df["mergedPRs"],
            title="Heatmap (densidade) — Estrelas × PRs mesclados",
            xlabel="Estrelas (stargazerCount)",
            ylabel="PRs mesclados (mergedPRs)",
            outpath=os.path.join(charts_dir, "heatmap_estrelas_vs_mergedPRs.png"),
            bins=40,
        )
    elif "releases" in df.columns and "mergedPRs" in df.columns:
        _plot_heatmap_2d(
            df["releases"],
            df["mergedPRs"],
            title="Heatmap (densidade) — Releases × PRs mesclados",
            xlabel="Releases",
            ylabel="PRs mesclados (mergedPRs)",
            outpath=os.path.join(charts_dir, "heatmap_releases_vs_mergedPRs.png"),
            bins=40,
        )

    print(f"[OK] Gráficos exploratórios salvos em: {charts_dir}")
