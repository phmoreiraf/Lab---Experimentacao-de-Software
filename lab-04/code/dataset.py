# dataset.py — Coleta de dados (OpenAQ) e processamento em tabelas diárias.
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import pandas as pd
from openaq_api import CAPITAIS, fetch_cities_measurements, load_cidades_500k

# Pastas
BASE = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(DATA, "raw")
PROC = os.path.join(DATA, "processed")
os.makedirs(RAW, exist_ok=True)
os.makedirs(PROC, exist_ok=True)

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _resolve_city_set(city_set: str,
                      custom: Optional[str] = None) -> List[Tuple[str, str]]:
    city_set = (city_set or "").strip().upper()
    if city_set in {"CAPITAIS", "CAPITAL", "CAP"}:
        return CAPITAIS
    if city_set in {"500K", "500+", "GRANDES"}:
        return load_cidades_500k()
    if city_set in {"CUSTOM", "PERSONALIZADO"} and custom:
        # formato: "SP:São Paulo;RJ:Rio de Janeiro;MG:Belo Horizonte"
        pairs = []
        for token in custom.split(";"):
            token = token.strip()
            if not token:
                continue
            if ":" in token:
                uf, city = token.split(":", 1)
                pairs.append((uf.strip(), city.strip()))
        return pairs
    # padrão: 500K
    return load_cidades_500k()

def fetch_latest_measurements(days: int = 365, city_set: str = "500K",
                              custom_cities: Optional[str] = None) -> pd.DataFrame:
    """
    Coleta últimos N dias de PM2.5/PM10 para o conjunto de cidades escolhido.
    Saída: data/raw/openaq_brazil_cities.csv
    """
    date_to = _now_utc()
    date_from = date_to - timedelta(days=days)
    date_from_iso = date_from.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_to_iso = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

    cities = _resolve_city_set(city_set, custom_cities)
    if not cities:
        # fallback — capitais
        cities = CAPITAIS

    df = fetch_cities_measurements(cities=cities,
                                   date_from_iso=date_from_iso,
                                   date_to_iso=date_to_iso)
    out = os.path.join(RAW, "openaq_brazil_cities.csv")
    df.to_csv(out, index=False)
    return df

def build_daily_tables() -> Dict[str, pd.DataFrame]:
    """
    Gera:
      - dim_city (lat/lon, UF, capital?)
      - daily_city_parameter (média/máx/contagem por dia/cidade/parâmetro)
    """
    src = os.path.join(RAW, "openaq_brazil_cities.csv")
    if not os.path.isfile(src):
        raise FileNotFoundError("Bruto não encontrado. Rode a coleta (make fetch ou menu opção 1).")

    df = pd.read_csv(src, parse_dates=["date.local", "date.utc"])
    # Normalização
    df = df[(df["value"].notna()) & (df["value"] >= 0)].copy()
    df["date"] = pd.to_datetime(df["date.local"]).dt.date
    df["is_capital"] = df.apply(
        lambda r: any((r["uf"], r["city"]) == cap for cap in CAPITAIS), axis=1
    )

    dim_city = (
        df.groupby(["city", "uf", "is_capital"])
          .agg(latitude=("coordinates.latitude", "mean"),
               longitude=("coordinates.longitude", "mean"))
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
