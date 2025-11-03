# dataset.py
# Coleta de dados (OpenAQ) e processamento em tabelas diárias.

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import pandas as pd
from gh_api import CAPITAIS, fetch_city_measurements

# Pastas
BASE = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(DATA, "raw")
PROC = os.path.join(DATA, "processed")

os.makedirs(RAW, exist_ok=True)
os.makedirs(PROC, exist_ok=True)

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def fetch_latest_measurements(days: int = 180) -> pd.DataFrame:
    """
    Coleta últimos N dias de PM2.5/PM10 para capitais do BR e salva CSV bruto.
    Saída: data/raw/openaq_brazil_capitals.csv
    """
    date_to = _now_utc()
    date_from = date_to - timedelta(days=days)
    date_from_iso = date_from.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_to_iso = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

    frames: List[pd.DataFrame] = []
    for uf, city in CAPITAIS:
        results = fetch_city_measurements(city=city, date_from_iso=date_from_iso, date_to_iso=date_to_iso)
        if not results:
            continue
        dfc = pd.json_normalize(results)
        dfc["uf"], dfc["city"] = uf, city
        frames.append(dfc)

    raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    out = os.path.join(RAW, "openaq_brazil_capitals.csv")
    if raw.empty:
        raw.to_csv(out, index=False)
        return raw

    keep = [
        "value", "unit", "parameter",
        "date.utc", "date.local",
        "location", "country",
        "coordinates.latitude", "coordinates.longitude",
        "city", "uf",
    ]
    for k in keep:
        if k not in raw.columns:
            raw[k] = None

    raw = raw[keep].rename(columns={
        "date.utc": "datetime_utc",
        "date.local": "datetime_local",
        "coordinates.latitude": "latitude",
        "coordinates.longitude": "longitude",
    })
    raw.to_csv(out, index=False)
    return raw

def build_daily_tables() -> Dict[str, pd.DataFrame]:
    """
    Gera:
      - dim_city (lat/lon por cidade/UF)
      - daily_city_parameter (média/máx/contagem por dia/cidade/parâmetro)
    Saídas em data/processed/
    """
    src = os.path.join(RAW, "openaq_brazil_capitals.csv")
    if not os.path.isfile(src):
        raise FileNotFoundError("Bruto não encontrado. Rode a coleta (make fetch ou menu opção 1).")

    df = pd.read_csv(src, parse_dates=["datetime_utc", "datetime_local"])
    df = df[(df["value"].notna()) & (df["value"] >= 0)].copy()
    df["date"] = df["datetime_local"].dt.date

    dim_city = (
        df.groupby(["city", "uf"])
          .agg(latitude=("latitude", "mean"), longitude=("longitude", "mean"))
          .reset_index()
    )

    daily = (
        df.groupby(["date", "city", "uf", "parameter", "unit"])
          .agg(mean_value=("value", "mean"),
               max_value=("value", "max"),
               n_measurements=("value", "count"))
          .reset_index()
    )

    dim_city.to_csv(os.path.join(PROC, "dim_city.csv"), index=False)
    daily.to_csv(os.path.join(PROC, "daily_city_parameter.csv"), index=False)
    return {"dim_city": dim_city, "daily": daily}
