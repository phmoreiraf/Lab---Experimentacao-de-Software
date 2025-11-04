# gh_api.py — integração direta com OpenAQ API v3 via requests
import os
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
OPENAQ_API_TOKEN = os.getenv("OPENAQ_API_TOKEN")

BASE_URL = "https://api.openaq.org/v3"
BRAZIL_ID = 45
TARGET_PARAMETERS = {"pm25", "pm10"}
HEADERS = {"X-API-Key": f"{OPENAQ_API_TOKEN}"}

# lista oficial de capitais brasileiras
CAPITAIS = [
    "Rio Branco", "Maceió", "Manaus", "Macapá", "Salvador", "Fortaleza", "Brasília",
    "Vitória", "Goiânia", "São Luís", "Cuiabá", "Campo Grande", "Belo Horizonte",
    "Belém", "João Pessoa", "Curitiba", "Recife", "Teresina", "Rio de Janeiro", "Natal",
    "Porto Alegre", "Porto Velho", "Boa Vista", "Florianópolis", "Aracaju", "São Paulo", "Palmas"
]


# =========================================================
# Funções utilitárias
# =========================================================

def get_brazil_locations(limit: int = 100) -> List[Dict]:
    """Busca todas as locations (estações) no Brasil."""
    print("[INFO] Buscando locations do Brasil...")
    all_locations = []
    page = 1

    while True:
        resp = requests.get(
            f"{BASE_URL}/locations",
            params={"countries_id": BRAZIL_ID, "limit": limit, "page": page},
            timeout=20,
            headers=HEADERS
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Erro ao buscar locations: {resp.text}")
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        all_locations.extend(results)
        meta = data.get("meta", {})
        found = meta.get("found", len(all_locations))
        if page * limit >= found:
            break
        page += 1
        time.sleep(0.3)
    print(f"[INFO] Total de {len(all_locations)} locations encontradas.")
    return all_locations


def filter_capitals_locations(locations: List[Dict]) -> List[Dict]:
    """Filtra as locations que pertencem às capitais brasileiras."""
    capitals_lower = {c.lower() for c in CAPITAIS}
    filtered = []
    for loc in locations:
        name = (loc.get("locality") or loc.get("name") or "").lower()
        if any(cap in name for cap in capitals_lower):
            filtered.append(loc)
    print(f"[INFO] {len(filtered)} locations pertencem às capitais brasileiras.")
    return filtered


def fetch_sensor_daily(sensor_id: int,
                       datetime_from: str,
                       datetime_to: str) -> List[Dict]:
    """Busca medições diárias para um sensor."""
    url = f"{BASE_URL}/sensors/{sensor_id}/measurements/daily"
    params = {
        "datetime_from": datetime_from,
        "datetime_to": datetime_to,
        "limit": 1000,
        "page": 1
    }
    records = []
    while True:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"[WARN] Falha no sensor {sensor_id}: {resp.text}")
            break
        data = resp.json()
        results = data.get("results", [])
        if not results:
            print(f"[INFO] Nenhum dado para sensor {sensor_id}.")
            break
        for item in results:
            records.append({
                "sensor_id": sensor_id,
                "date_utc": item.get("datetime", {}).get("utc"),
                "date_local": item.get("datetime", {}).get("local"),
                "value": item.get("value"),
                "unit": item.get("unit"),
            })
        meta = data.get("meta", {})
        found = meta.get("found", len(records))
        if params["page"] * params["limit"] >= found:
            break
        params["page"] += 1
        time.sleep(0.2)
    return records


# =========================================================
# Pipeline principal
# =========================================================

def fetch_capitais_measurements(days: int = 180,
                                max_capitais: Optional[int] = None) -> pd.DataFrame:
    """
    1. Lista locations do Brasil.
    2. Filtra apenas capitais.
    3. Busca sensores PM2.5 e PM10.
    4. Coleta medições diárias de cada sensor.
    5. Retorna DataFrame consolidado.
    """
    date_to = datetime.now(timezone.utc)
    date_from = date_to - timedelta(days=days)
    date_from_iso = date_from.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_to_iso = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"[INFO] Coletando medições de {date_from_iso} até {date_to_iso}")

    locations = get_brazil_locations()
    capital_locs = filter_capitals_locations(locations)
    if max_capitais:
        capital_locs = capital_locs[:max_capitais]

    all_records = []

    for loc in capital_locs:
        loc_id = loc["id"]
        loc_name = loc["name"]
        city = loc.get("locality") or loc["name"]
        coords = loc.get("coordinates", {})
        sensors = loc.get("sensors", [])
        for sensor in sensors:
            param = sensor.get("parameter", {}).get("name", "").lower()
            if param not in TARGET_PARAMETERS:
                continue
            sid = sensor["id"]
            unit = sensor.get("parameter", {}).get("units")
            records = fetch_sensor_daily(sid, date_from_iso, date_to_iso)
            for r in records:
                all_records.append({
                    "location_id": loc_id,
                    "location_name": loc_name,
                    "city": city,
                    "latitude": coords.get("latitude"),
                    "longitude": coords.get("longitude"),
                    "sensor_id": sid,
                    "parameter": param,
                    "value": r["value"],
                    "unit": r["unit"] or unit,
                    "date_utc": r["date_utc"],
                    "date_local": r["date_local"]
                })
        time.sleep(0.3)

    df = pd.DataFrame(all_records)
    print(f"[INFO] Total de registros coletados: {len(df)}")
    return df
