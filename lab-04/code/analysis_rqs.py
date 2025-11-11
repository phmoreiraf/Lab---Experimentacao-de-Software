# analysis_rqs.py — Exporta artefatos para BI e gera relatório (i–iv) com RQs e testes
import os
from datetime import datetime as _dt
from typing import Dict

import pandas as pd

# Pastas
BASE = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.join(BASE, "data")
PROC = os.path.join(DATA, "processed")
BI = os.path.join(DATA, "bi")
DOCS = os.path.join(BASE, "docs")
PLOTS = os.path.join(DOCS, "plots")

os.makedirs(BI, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)
os.makedirs(PLOTS, exist_ok=True)

THRESHOLDS = {"pm25": [15.0, 25.0], "pm10": [45.0, 50.0]}  # µg/m³ (OMS/WHO 2021 — 24h)

def _dim_time(dates: pd.Series) -> pd.DataFrame:
    s = pd.to_datetime(dates).dropna()
    return pd.DataFrame({
        "date": s.dt.date.astype(str),
        "year": s.dt.year,
        "month": s.dt.month,
        "month_name": s.dt.month_name(),
        "quarter": s.dt.quarter,
        "week": s.dt.isocalendar().week.astype(int),
        "dow": s.dt.dayofweek,
        "dow_name": s.dt.day_name(),
    }).drop_duplicates()

def _plot_helpers():
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.figsize": (9, 4), "axes.grid": True})
    return plt

def build_bi_outputs() -> Dict[str, pd.DataFrame]:
    daily_path = os.path.join(PROC, "daily_city_parameter.csv")
    dim_city_path = os.path.join(PROC, "dim_city.csv")
    if not (os.path.isfile(daily_path) and os.path.isfile(dim_city_path)):
        raise FileNotFoundError("Arquivos processados não encontrados. Rode 'make process' antes.")

    daily = pd.read_csv(daily_path, parse_dates=["date"])
    dim_city = pd.read_csv(dim_city_path)

    fact = daily.rename(columns={"mean_value": "value_mean"}).copy()
    fact["date"] = pd.to_datetime(fact["date"]).dt.date.astype(str)

    dim_time = _dim_time(pd.to_datetime(daily["date"]))
    dim_parameter = pd.DataFrame({
        "parameter": ["pm25", "pm10"],
        "description": ["Particulate Matter ≤2.5µm", "Particulate Matter ≤10µm"],
        "unit": ["µg/m³", "µg/m³"],
    })

    agg_rank = (
        daily.groupby(["city", "uf", "parameter"])
             .agg(mean_value=("mean_value", "mean"),
                  days=("date", "nunique"))
             .reset_index()
             .sort_values(["parameter", "mean_value"], ascending=[True, False])
    )

    rows = []
    for prm, thrs in THRESHOLDS.items():
        sub = daily[daily["parameter"] == prm]
        if sub.empty:
            continue
        g = sub.groupby(["city", "uf"])
        total = g["date"].nunique()
        for thr in thrs:
            exc = g.apply(lambda t: (t["mean_value"] > thr).sum())
            tmp = pd.DataFrame({
                "city": total.index.get_level_values("city"),
                "uf": total.index.get_level_values("uf"),
                "parameter": prm,
                "threshold": thr,
                "days_total": total.values,
                "days_exceeded": exc.values,
            })
            tmp["exceed_rate_pct"] = (tmp["days_exceeded"] / tmp["days_total"] * 100).round(2)
            rows.append(tmp)
    agg_exceed = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(
        columns=["city", "uf", "parameter", "threshold", "days_total", "days_exceeded", "exceed_rate_pct"]
    )

    # salva BI
    fact.to_csv(os.path.join(BI, "fact_air_quality.csv"), index=False)
    dim_city.to_csv(os.path.join(BI, "dim_city.csv"), index=False)
    dim_time.to_csv(os.path.join(BI, "dim_time.csv"), index=False)
    dim_parameter.to_csv(os.path.join(BI, "dim_parameter.csv"), index=False)
    agg_rank.to_csv(os.path.join(BI, "agg_rank_city.csv"), index=False)
    agg_exceed.to_csv(os.path.join(BI, "agg_exceedance.csv"), index=False)

    return {
        "fact": fact,
        "dim_city": dim_city,
        "dim_time": dim_time,
        "dim_parameter": dim_parameter,
        "agg_rank": agg_rank,
        "agg_exceed": agg_exceed,
    }

# ------------------ RQs e testes de hipótese ------------------

def _tests_and_plots(fact: pd.DataFrame, dim_city: pd.DataFrame) -> pd.DataFrame:
    """
    RQ1: Capitais vs. Grandes cidades (500k+) diferem em PM2.5/PM10?
    RQ2: Houve mudança entre a 1ª metade do período e a 2ª metade?
    Salva gráficos em docs/plots e retorna tabela de testes.
    """
    from scipy.stats import mannwhitneyu

    # Merge para obter is_capital
    dc = dim_city[["city", "uf", "is_capital"]] if "is_capital" in dim_city.columns else dim_city.assign(is_capital=False)
    df = fact.merge(dc, on=["city", "uf"], how="left")
    df["is_capital"] = df["is_capital"].fillna(False)

    df["date_dt"] = pd.to_datetime(df["date"])
    mid_date = df["date_dt"].min() + (df["date_dt"].max() - df["date_dt"].min()) / 2
    df["period_half"] = (df["date_dt"] > mid_date).map({True: "late", False: "early"})

    results = []

    # ---------- RQ1 ----------
    for prm in ["pm25", "pm10"]:
        sub = df[df["parameter"] == prm]
        g_cap = sub[sub["is_capital"]]["value_mean"].dropna().values
        g_big = sub[~sub["is_capital"]]["value_mean"].dropna().values
        if len(g_cap) > 0 and len(g_big) > 0:
            u = mannwhitneyu(g_cap, g_big, alternative="two-sided")
            n1, n2 = len(g_cap), len(g_big)
            r_rb = 1 - (2 * u.statistic) / (n1 * n2)  # rank-biserial (sinal indica direção)
            results.append({
                "rq": "RQ1",
                "hypothesis": "Capitais vs. grandes cidades (>500k) têm distribuição diferente",
                "parameter": prm,
                "test": "Mann–Whitney U",
                "n_cap": n1, "n_500k": n2,
                "U": float(u.statistic), "p_value": float(u.pvalue),
                "rank_biserial": float(r_rb),
            })

    # ---------- RQ2 ----------
    for prm in ["pm25", "pm10"]:
        sub = df[df["parameter"] == prm]
        early = sub[sub["period_half"] == "early"]["value_mean"].dropna().values
        late = sub[sub["period_half"] == "late"]["value_mean"].dropna().values
        if len(early) > 0 and len(late) > 0:
            u = mannwhitneyu(early, late, alternative="two-sided")
            n1, n2 = len(early), len(late)
            r_rb = 1 - (2 * u.statistic) / (n1 * n2)
            results.append({
                "rq": "RQ2",
                "hypothesis": "1ª metade vs. 2ª metade têm distribuição diferente",
                "parameter": prm,
                "test": "Mann–Whitney U",
                "n_early": n1, "n_late": n2,
                "U": float(u.statistic), "p_value": float(u.pvalue),
                "rank_biserial": float(r_rb),
            })

    # ---------- Gráficos ----------
    try:
        plt = _plot_helpers()
        # Densidade por grupo (PM2.5)
        prm = "pm25"
        sub = df[df["parameter"] == prm]
        if not sub.empty:
            ax = sub[sub["is_capital"] == True]["value_mean"].plot(kind="kde", linewidth=2, label="Capitais")
            sub[sub["is_capital"] == False]["value_mean"].plot(kind="kde", linewidth=2, label="Grandes (>500k)", ax=ax)
            ax.set_title("Densidade PM2.5 — Capitais vs. Grandes (>500k)")
            ax.set_xlabel("µg/m³")
            ax.legend()
            p1 = os.path.join(PLOTS, "density_pm25_cap_vs_500k.png")
            plt.tight_layout(); plt.savefig(p1, dpi=140); plt.clf()

        # Série temporal (média diária por data) — top 5 cidades com maiores médias em PM2.5
        pm25_rank = (df[df["parameter"] == "pm25"]
                        .groupby(["city", "uf"])
                        ["value_mean"].mean().sort_values(ascending=False).head(5))
        if not pm25_rank.empty:
            for (city, uf) in pm25_rank.index:
                series = (df[(df["parameter"] == "pm25") & (df["city"] == city) & (df["uf"] == uf)]
                          .sort_values("date_dt").groupby("date_dt")["value_mean"].mean())
                series.plot(linewidth=1.5, label=f"{city}/{uf}")
            import matplotlib.pyplot as plt_m
            plt_m.title("PM2.5 — Média diária (Top 5 cidades)")
            plt_m.xlabel("Data"); plt_m.ylabel("µg/m³")
            plt_m.legend()
            p2 = os.path.join(PLOTS, "ts_pm25_top5.png")
            plt_m.tight_layout(); plt_m.savefig(p2, dpi=140); plt_m.clf()
    except Exception:
        # Mantém o pipeline mesmo sem renderizar gráficos (ex.: ambiente sem display)
        pass

    tests_df = pd.DataFrame(results)
    tests_df.to_csv(os.path.join(BI, "hypothesis_tests.csv"), index=False)
    return tests_df

def generate_report_md(path: str = os.path.join(DOCS, "report_alt.md")) -> str:
    """Gera relatório com as 4 seções obrigatórias (i–iv) + RQs e testes."""
    def _read(p: str) -> pd.DataFrame:
        return pd.read_csv(p) if os.path.isfile(p) else pd.DataFrame()

    fact = _read(os.path.join(BI, "fact_air_quality.csv"))
    dim_city = _read(os.path.join(BI, "dim_city.csv"))
    dim_time = _read(os.path.join(BI, "dim_time.csv"))
    agg_rank = _read(os.path.join(BI, "agg_rank_city.csv"))
    agg_exc = _read(os.path.join(BI, "agg_exceedance.csv"))

    n_medicoes = len(fact)
    n_cidades = dim_city["city"].nunique() if not dim_city.empty else 0
    period = ""
    if not dim_time.empty:
        xs = dim_time["date"].astype(str)
        period = f"{xs.min()} a {xs.max()}"

    top_pm25 = ""
    if not agg_rank.empty:
        pm25 = agg_rank[agg_rank["parameter"] == "pm25"].sort_values("mean_value", ascending=False).head(3)
        if not pm25.empty:
            top_pm25 = "; ".join([f"{r.city}/{r.uf} ({r.mean_value:.1f} µg/m³)" for _, r in pm25.iterrows()])

    # RQs e testes
    tests_df = _tests_and_plots(fact, dim_city) if not fact.empty and not dim_city.empty else pd.DataFrame()

    lines = []
    lines.append("# Relatório — Visualização de Dados com BI (Trabalho Alternativo)\n")
    lines.append(f"*Gerado em*: {_dt.now().strftime('%Y-%m-%d %H:%M')}\n")

    # (i) Introdução
    lines.append("## 1. Introdução\n")
    lines.append("Este relatório apresenta um dashboard construído a partir de dados públicos de qualidade do ar (OpenAQ v3) para **capitais e grandes cidades brasileiras (>500 mil habitantes)**. O objetivo é disponibilizar visualizações e estatísticas que apoiem a análise comparativa entre recortes geográficos e temporais.\n")

    # (ii) Metodologia/Descrição da base
    lines.append("## 2. Metodologia e Descrição da Base\n")
    lines.append("- **Fonte**: OpenAQ v3 (parâmetros PM2.5 e PM10). Coleta via API REST (agregação **diária por sensor**) consolidada por **cidade**.\n")
    lines.append("- **Processamento**: consolidação **diária por cidade/parâmetro** (média, máximo, contagem); modelagem **fato/dimensão**; agregados (ranking e excedências por limiares OMS/WHO 2021 — 24h).\n")
    lines.append(f"- **Período**: {period if period else '*indisponível*'}; **Cidades**: {n_cidades}; **Fato**: {n_medicoes} linhas.\n")

    # RQs
    lines.append("### 2.1 Questões de Pesquisa (RQs)\n")
    lines.append("- **RQ1** — Existe diferença na distribuição das concentrações diárias de **PM2.5/PM10** entre **capitais** e **grandes cidades (>500k)**?\n")
    lines.append("- **RQ2** — Há diferença entre a **primeira** e a **segunda metade** do período analisado para **PM2.5/PM10**?\n")

    # (iii) Resultados
    lines.append("## 3. Resultados\n")
    lines.append("- **Caracterização**: KPIs, mapa por cidade e séries temporais por parâmetro no dashboard.\n")
    lines.append(f"- **Ranking (PM2.5)** — Top 3 médias: {top_pm25 if top_pm25 else '*indisponível*'}.\n")
    lines.append("- **Excedências**: % de dias acima de limiares (PM2.5: 15/25; PM10: 45/50 µg/m³) por cidade/período.\n")

    # Testes
    if not tests_df.empty:
        lines.append("### 3.1 Testes de Hipóteses\n")
        for _, r in tests_df.iterrows():
            desc = f"**{r['rq']} / {r['parameter'].upper()}** — {r['test']} (U={r['U']:.1f}, p={r['p_value']:.3g}, r_rb={r['rank_biserial']:.3f})."
            lines.append(f"- {desc}\n")
        # Imagens, se geradas
        for img in ["density_pm25_cap_vs_500k.png", "ts_pm25_top5.png"]:
            p = os.path.join("plots", img)
            if os.path.isfile(os.path.join(DOCS, p)):
                lines.append(f"![{img}]({p})\n")

    # (iv) Discussão
    lines.append("## 4. Discussão\n")
    lines.append("Os resultados indicam padrões geográficos e temporais em material particulado, com limitações decorrentes de cobertura heterogênea de sensores e lacunas de dados em algumas cidades >500k. Próximos passos: enriquecer com variáveis climáticas, mobilidade urbana e focos de queimadas (INPE), além de análises sazonais e modelos de séries temporais.\n")

    path = path or os.path.join(DOCS, "report_alt.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path
