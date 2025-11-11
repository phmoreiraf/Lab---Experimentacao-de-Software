# openaq_api.py — integração com OpenAQ API v3 (coleta diária por sensor + consolidação por cidade)
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
OPENAQ_API_TOKEN = os.getenv("OPENAQ_API_TOKEN")
BASE_URL = "https://api.openaq.org/v3"
BRAZIL_ID = 45
TARGET_PARAMETERS = {"pm25", "pm10"}
HEADERS = {"X-API-Key": f"{OPENAQ_API_TOKEN}"} if OPENAQ_API_TOKEN else {}

# --- Lista de capitais (UF, cidade) ---
CAPITAIS: List[Tuple[str, str]] = [
    ("AC", "Rio Branco"), ("AL", "Maceió"), ("AM", "Manaus"), ("AP", "Macapá"),
    ("BA", "Salvador"), ("CE", "Fortaleza"), ("DF", "Brasília"), ("ES", "Vitória"),
    ("GO", "Goiânia"), ("MA", "São Luís"), ("MT", "Cuiabá"), ("MS", "Campo Grande"),
    ("MG", "Belo Horizonte"), ("PA", "Belém"), ("PB", "João Pessoa"), ("PR", "Curitiba"),
    ("PE", "Recife"), ("PI", "Teresina"), ("RJ", "Rio de Janeiro"), ("RN", "Natal"),
    ("RS", "Porto Alegre"), ("RO", "Porto Velho"), ("RR", "Boa Vista"), ("SC", "Florianópolis"),
    ("SE", "Aracaju"), ("SP", "São Paulo"), ("TO", "Palmas"),
]

# --- Cidades brasileiras com população > 500 mil (IBGE – base prática para coleta) ---
# Obs.: criamos também um CSV editável em runtime (data/cities_500k.csv) para você personalizar facilmente.
DEFAULT_CIDADES_500K: List[Tuple[str, str]] = [
    # Capitais (>=500k) já inseridas
    ("SP", "São Paulo"), ("RJ", "Rio de Janeiro"), ("BA", "Salvador"), ("CE", "Fortaleza"),
    ("MG", "Belo Horizonte"), ("AM", "Manaus"), ("PR", "Curitiba"), ("PE", "Recife"),
    ("GO", "Goiânia"), ("PA", "Belém"), ("RS", "Porto Alegre"), ("RN", "Natal"),
    ("MA", "São Luís"), ("AL", "Maceió"), ("PB", "João Pessoa"), ("PI", "Teresina"),
    ("MT", "Cuiabá"), ("MS", "Campo Grande"), ("SE", "Aracaju"), ("SC", "Florianópolis"),
    ("RO", "Porto Velho"), ("AP", "Macapá"),
    # Não-capitais (>=500k) — principais
    ("SP", "Guarulhos"), ("SP", "Campinas"), ("RJ", "São Gonçalo"), ("RJ", "Duque de Caxias"),
    ("RJ", "Nova Iguaçu"), ("SP", "São Bernardo do Campo"), ("SP", "Santo André"),
    ("SP", "Osasco"), ("SP", "São José dos Campos"), ("SP", "Sorocaba"),
    ("SP", "Ribeirão Preto"), ("PE", "Jaboatão dos Guararapes"), ("MG", "Contagem"),
    ("MG", "Uberlândia"), ("MG", "Juiz de Fora"), ("ES", "Serra"), ("ES", "Vila Velha"),
    ("PR", "Londrina"), ("SC", "Joinville"), ("RS", "Caxias do Sul"), ("GO", "Aparecida de Goiânia"),
    ("PA", "Ananindeua"), ("RJ", "Belford Roxo"), ("RJ", "Campos dos Goytacazes"),
    ("BA", "Feira de Santana"),
]

def _city_csv_path() -> str:
    base = os.path.abspath(os.path.dirname(__file__))
    data = os.path.join(base, "data")
    os.makedirs(data, exist_ok=True)
    return os.path.join(data, "cities_500k.csv")

def load_cidades_500k() -> List[Tuple[str, str]]:
    """
    Carrega data/cities_500k.csv (UF,cidade). Se não existir, cria com DEFAULT_CIDADES_500K.
    """
    path = _city_csv_path()
    if not os.path.isfile(path):
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["uf", "city"])
            for uf, c in DEFAULT_CIDADES_500K:
                w.writerow([uf, c])
    df = pd.read_csv(path, dtype=str)
    df = df.dropna(subset=["uf", "city"])
    cidades = [(r.uf.strip(), r.city.strip()) for _, r in df.iterrows()]
    return cidades

def get_brazil_locations(limit: int = 1000) -> List[Dict]:
    """Busca todas as locations do Brasil (com sensores embutidos quando disponível)."""
    all_locations = []
    page = 1
    while True:
        resp = requests.get(
            f"{BASE_URL}/locations",
            params={"countries_id": BRAZIL_ID, "limit": limit, "page": page},
            timeout=30,
            headers=HEADERS or None,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Erro ao buscar locations: {resp.text}")
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        all_locations.extend(results)
        found = data.get("meta", {}).get("found", len(all_locations))
        if page * limit >= found:
            break
        page += 1
        time.sleep(0.25)
    return all_locations

def fetch_sensor_daily(sensor_id: int, datetime_from: str, datetime_to: str) -> List[Dict]:
    """Medições diárias agregadas por sensor."""
    url = f"{BASE_URL}/sensors/{sensor_id}/measurements/daily"
    params = {"datetime_from": datetime_from, "datetime_to": datetime_to, "limit": 1000, "page": 1}
    out: List[Dict] = []
    while True:
        resp = requests.get(url, headers=HEADERS or None, params=params, timeout=40)
        if resp.status_code != 200:
            break
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        for item in results:
            out.append({
                "date.utc": item.get("datetime", {}).get("utc"),
                "date.local": item.get("datetime", {}).get("local"),
                "value": item.get("value"),
                "unit": item.get("unit"),
            })
        meta = data.get("meta", {})
        found = meta.get("found", len(out))
        if params["page"] * params["limit"] >= found:
            break
        params["page"] += 1
        time.sleep(0.2)
    return out

def fetch_cities_measurements(cities: List[Tuple[str, str]],
                              date_from_iso: str,
                              date_to_iso: str) -> pd.DataFrame:
    """
    Coleta medições diárias (PM2.5/PM10) para a lista (UF, cidade).
    Retorna DataFrame normalizado com colunas compatíveis ao pipeline.
    """
    locs = get_brazil_locations()
    # Índice por 'locality' e 'name' (minúsculos) -> lista de locations
    buckets: Dict[str, List[Dict]] = {}
    for loc in locs:
        key1 = (loc.get("locality") or "").strip().lower()
        key2 = (loc.get("name") or "").strip().lower()
        for k in {key1, key2}:
            if not k:
                continue
            buckets.setdefault(k, []).append(loc)

    rows = []
    for uf, city in cities:
        key = city.lower()
        for loc in buckets.get(key, []):
            coords = loc.get("coordinates", {}) or {}
            sensors = loc.get("sensors", []) or []
            for s in sensors:
                param = (s.get("parameter", {}) or {}).get("name", "").lower()
                if param not in TARGET_PARAMETERS:
                    continue
                sid = s.get("id")
                unit = (s.get("parameter", {}) or {}).get("units")
                recs = fetch_sensor_daily(sid, date_from_iso, date_to_iso)
                for r in recs:
                    rows.append({
                        "value": r.get("value"),
                        "unit": r.get("unit") or unit,
                        "parameter": param,
                        "date.utc": r.get("date.utc"),
                        "date.local": r.get("date.local"),
                        "location": loc.get("name"),
                        "country": "BR",
                        "coordinates.latitude": coords.get("latitude"),
                        "coordinates.longitude": coords.get("longitude"),
                        "city": city,
                        "uf": uf,
                    })
        time.sleep(0.2)
    return pd.DataFrame(rows)
