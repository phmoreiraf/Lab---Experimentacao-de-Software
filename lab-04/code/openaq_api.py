from dotenv import load_dotenv
import requests
import pandas as pd
import time
import dotenv
import os

# -----------------------------------------------
# CONFIGURAÇÕES
# -----------------------------------------------
load_dotenv()
API_KEY = os.getenv("OPENAQ_API_TOKEN")
BASE_URL = "https://api.openaq.org/v3"
radius = 12000   # tamanho do raio em metros em redor do ponto central
WAIT = 1.0    # segundos de espera entre requisições (evita rate limit)
COUNTRY_ID = 45      # Brasil

DIR_SENSORS_DATA = os.path.join("data", "raw")
os.makedirs(DIR_SENSORS_DATA, exist_ok=True)

# -----------------------------------------------
# LISTA DE CIDADES GRANDES DO BRASIL (≥ 500 mil hab)
# -----------------------------------------------
cities = [
    {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333},
    {"name": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729},
    {"name": "Brasília", "lat": -15.8267, "lon": -47.9218},
    {"name": "Fortaleza", "lat": -3.7319, "lon": -38.5267},
    {"name": "Salvador", "lat": -12.9777, "lon": -38.5016},
    {"name": "Belo Horizonte", "lat": -19.9167, "lon": -43.9345},
    {"name": "Manaus", "lat": -3.1190, "lon": -60.0217},
    {"name": "Curitiba", "lat": -25.4296, "lon": -49.2713},
    {"name": "Recife", "lat": -8.0476, "lon": -34.8770},
    {"name": "Porto Alegre", "lat": -30.0346, "lon": -51.2177},
    {"name": "Belém", "lat": -1.4550, "lon": -48.5020},
    {"name": "Goiânia", "lat": -16.6869, "lon": -49.2648},
    {"name": "Guarulhos", "lat": -23.4543, "lon": -46.5337},
    {"name": "Campinas", "lat": -22.9056, "lon": -47.0608},
    {"name": "São Luís", "lat": -2.5297, "lon": -44.3028},
    {"name": "São Gonçalo", "lat": -22.8268, "lon": -43.0634},
    {"name": "Maceió", "lat": -9.6659, "lon": -35.7350},
    {"name": "Duque de Caxias", "lat": -22.7859, "lon": -43.3117},
    {"name": "Natal", "lat": -5.7945, "lon": -35.2110},
    {"name": "Campo Grande", "lat": -20.4697, "lon": -54.6201},
    {"name": "Teresina", "lat": -5.0892, "lon": -42.8019},
    {"name": "São Bernardo do Campo", "lat": -23.6939, "lon": -46.5650},
    {"name": "Nova Iguaçu", "lat": -22.7557, "lon": -43.4608},
    {"name": "João Pessoa", "lat": -7.1150, "lon": -34.8631},
    {"name": "Santo André", "lat": -23.6639, "lon": -46.5383},
    {"name": "Osasco", "lat": -23.5329, "lon": -46.7910},
    {"name": "Jaboatão dos Guararapes", "lat": -8.1120, "lon": -35.0140},
    {"name": "Ribeirão Preto", "lat": -21.1775, "lon": -47.8103},
    {"name": "Uberlândia", "lat": -18.9186, "lon": -48.2772},
    {"name": "Contagem", "lat": -19.9320, "lon": -44.0539},
    {"name": "Aracaju", "lat": -10.9111, "lon": -37.0717},
    {"name": "Feira de Santana", "lat": -12.2664, "lon": -38.9663},
    {"name": "Sorocaba", "lat": -23.5017, "lon": -47.4526},
    {"name": "Londrina", "lat": -23.3045, "lon": -51.1696},
    {"name": "Niterói", "lat": -22.8832, "lon": -43.1033}
]

# -----------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------

def fetch_locations_for_city(city):
    url = f"{BASE_URL}/locations?coordinates={city['lat']},{city['lon']}&radius={radius}&limit=500"
    headers = {"X-API-Key": API_KEY}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("results", [])
        return data
    except Exception as e:
        print(f"Erro em {city['name']}: {e}")
        return []

def fetch_sensor_yearly(sensor_id, date_from=None, date_to=None):
    url = f"{BASE_URL}/sensors/{sensor_id}/days/yearly"
    params = {"date_from": date_from, "date_to": date_to}
    headers = {"X-API-Key": API_KEY}
    try:
        resp = requests.get(url, headers=headers, params=params if date_from and date_to else None, timeout=30)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        print(f"Erro no sensor {sensor_id}: {e}")
        return []
# -----------------------------------------------
# COLETA DE DADOS
# -----------------------------------------------
def get_sensors_from_locations(locations):
    records = []
    known_sensors_ids = set()
    for city in cities:
        results = fetch_locations_for_city(city)
        print(f"{city['name']}: {len(results)} locais encontrados.")

        for loc in results:
            sensors = loc.get("sensors", [])
            for sensor in sensors:
                if sensor.get("id") in known_sensors_ids:
                    continue
                known_sensors_ids.add(sensor.get("id"))
                param = sensor.get("parameter", {})
                records.append({
                    "city": city["name"],
                    "location_id": loc.get("id"),
                    "location_name": loc.get("name"),
                    "locality": loc.get("locality"),
                    "country_name": loc.get("country", {}).get("name"),
                    "sensor_id": sensor.get("id"),
                    "sensor_name": sensor.get("name"),
                    "parameter_id": param.get("id"),
                    "parameter_name": param.get("name"),
                    "parameter_displayName": param.get("displayName"),
                    "parameter_units": param.get("units"),
                    "latitude": loc.get("coordinates", {}).get("latitude"),
                    "longitude": loc.get("coordinates", {}).get("longitude"),
                    "datetimeFirst_utc": loc.get("datetimeFirst", {}).get("utc") if loc.get("datetimeFirst") else None,
                    "datetimeLast_utc": loc.get("datetimeLast", {}).get("utc") if loc.get("datetimeLast") else None,
                })
        time.sleep(WAIT)
    return pd.DataFrame(records)

def get_sensor_yearly_data(df_sensors):
    records = []
    if df_sensors.empty:
        df_sensors = pd.read_csv(os.path.join(DIR_SENSORS_DATA, "openaq_brazil_sensors.csv"))

    for _, row in df_sensors.iterrows():
        sid = row["sensor_id"]
        city = row["city"]
        print(f"Coletando dados anuais do sensor {sid} ({city})...")

        yearly_data = fetch_sensor_yearly(sid)
        if not yearly_data:
            continue

        for year in yearly_data:
            param_data = year.get("parameter", {})
            period = year.get("period", {})
            summary = year.get("summary", {})
            coverage = year.get("coverage", {})

            records.append({
                "city": city,
                "sensor_id": sid,
                "parameter_name": param_data.get("name"),
                "units": param_data.get("units"),
                "value": year.get("value"),
                "avg": summary.get("avg"),
                "min": summary.get("min"),
                "max": summary.get("max"),
                "median": summary.get("median"),
                "datetimeFrom_utc": period.get("datetimeFrom", {}).get("utc"),
                "datetimeTo_utc": period.get("datetimeTo", {}).get("utc"),
                "percentCoverage": coverage.get("percentCoverage"),
                "observedCount": coverage.get("observedCount"),
                "expectedCount": coverage.get("expectedCount"),
            })
        time.sleep(WAIT)

    df_yearly = pd.DataFrame(records)
    path = os.path.join(DIR_SENSORS_DATA, "openaq_brazil_yearly.csv")
    df_yearly.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"\n Dados anuais salvos em: {path}")
    return df_yearly


# --------------------------------------------------
# SALVA RESULTADOS
# --------------------------------------------------
def save_to_csv(records: pd.DataFrame, filename, message=""):
    print(f"\n{message}")
    records.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"Arquivo salvo: {filename}")

def get_openaq_brazil_sensors():
    records = get_sensors_from_locations(cities)
    save_to_csv(records, os.path.join(DIR_SENSORS_DATA, "openaq_brazil_sensors.csv"), "Dados de sensores do OpenAQ no Brasil")
    return records

def get_openaq_brazil_yearly_data(df_sensors=None):
    df_yearly = get_sensor_yearly_data(df_sensors)
    save_to_csv(df_yearly, os.path.join(DIR_SENSORS_DATA, "openaq_brazil_yearly.csv"), "Dados anuais do OpenAQ no Brasil")
    return df_yearly

if __name__ == "__main__":
    df_sensors = get_openaq_brazil_sensors()
    get_openaq_brazil_yearly_data(df_sensors)