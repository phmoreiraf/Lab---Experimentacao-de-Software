# analysis_rqs.py
# Exporta artefatos para BI (fato/dimensões/aggregates) e gera relatório (i–iv).

import os
from typing import Dict

import pandas as pd

# Pastas
BASE = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.join(BASE, "data")
PROC = os.path.join(DATA, "processed")
BI = os.path.join(DATA, "bi")
DOCS = os.path.join(BASE, "docs")

os.makedirs(BI, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)

THRESHOLDS = {"pm25": [15.0, 25.0], "pm10": [45.0, 50.0]}  # µg/m³ (referência analítica)

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

def build_bi_outputs() -> Dict[str, pd.DataFrame]:
    """
    Lê processed, gera:
      - fact_air_quality.csv
      - dim_city.csv
      - dim_time.csv
      - dim_parameter.csv
      - agg_rank_city.csv
      - agg_exceedance.csv
    """

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

def generate_report_md(path: str = os.path.join(DOCS, "report_alt.md")) -> str:
    """
    Gera relatório com as 4 seções obrigatórias (i–iv) em Markdown.
    Lê os artefatos BI gerados previamente.
    """
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

    lines = []
    lines.append("# Relatório — Visualização de Dados com BI\n")
    from datetime import datetime as _dt
    lines.append(f"*Gerado em*: {_dt.now().strftime('%Y-%m-%d %H:%M')}\n")

    # (i) Introdução
    lines.append("## 1. Introdução\n")
    lines.append("Este relatório apresenta um dashboard construído a partir de dados públicos de qualidade do ar (OpenAQ v2) em capitais brasileiras.\n")

    # (ii) Metodologia/Descrição da base
    lines.append("## 2. Metodologia e Descrição da Base\n")
    lines.append("- **Fonte**: OpenAQ v2 (parâmetros PM2.5 e PM10). Coleta via API REST para capitais do Brasil nos últimos N dias.\n")
    lines.append("- **Processamento**: consolidação **diária por cidade/parâmetro** (média, máximo, contagem) e modelagem **fato/dimensão**.\n")
    lines.append(f"- **Período**: {period if period else '*indisponível*'}; **Cidades**: {n_cidades}; **Fato**: {n_medicoes} linhas.\n")

    # (iii) Resultados
    lines.append("## 3. Resultados\n")
    lines.append("- **Caracterização**: KPIs, mapa por cidade e séries temporais por parâmetro no dashboard.\n")
    lines.append("- **Ranking (PM2.5)** — Top 3 médias: " + (top_pm25 if top_pm25 else "*indisponível*") + ".\n")
    lines.append("- **Excedências**: % de dias acima de limiares (PM2.5: 15/25; PM10: 45/50 µg/m³) por cidade/período.\n")

    # (iv) Discussão
    lines.append("## 4. Discussão\n")
    lines.append("Interpretação dos padrões observados, limitações (cobertura heterogênea, disponibilidade de sensores) e próximos passos (integrar clima, mobilidade e queimadas — INPE).\n")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path
