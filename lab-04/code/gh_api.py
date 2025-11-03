# gh_api.py
# Mantido o nome do arquivo, mas agora serve de cliente para a API pública OpenAQ.

import time
from typing import Dict, List, Optional, Tuple

import requests

API = "https://api.openaq.org/v2/measurements"

# Capitais brasileiras
CAPITAIS: Tuple[Tuple[str, str], ...] = (
    ("AC", "Rio Branco"), ("AL", "Maceió"), ("AM", "Manaus"), ("AP", "Macapá"),
    ("BA", "Salvador"), ("CE", "Fortaleza"), ("DF", "Brasília"), ("ES", "Vitória"),
    ("GO", "Goiânia"), ("MA", "São Luís"), ("MG", "Belo Horizonte"),
    ("MS", "Campo Grande"), ("MT", "Cuiabá"), ("PA", "Belém"), ("PB", "João Pessoa"),
    ("PE", "Recife"), ("PI", "Teresina"), ("PR", "Curitiba"), ("RJ", "Rio de Janeiro"),
    ("RN", "Natal"), ("RO", "Porto Velho"), ("RR", "Boa Vista"), ("RS", "Porto Alegre"),
    ("SC", "Florianópolis"), ("SE", "Aracaju"), ("SP", "São Paulo"), ("TO", "Palmas"),
)

def fetch_city_measurements(
    city: str,
    country: str = "BR",
    parameters: Tuple[str, ...] = ("pm25", "pm10"),
    date_from_iso: Optional[str] = None,
    date_to_iso: Optional[str] = None,
    limit: int = 10000,
    sleep_seconds: float = 0.5,
    timeout_sec: int = 60,
) -> List[Dict]:
    """
    Baixa medições para uma cidade da API OpenAQ (pagina automaticamente).
    Retorna lista de dicts (JSON da API).
    """
    page, out = 1, []
    while True:
        params = {
            "country": country,
            "city": city,
            "parameter": ",".join(parameters),
            "page": page,
            "limit": 1000,
            "order_by": "datetime",
            "sort": "desc",
        }
        if date_from_iso:
            params["date_from"] = date_from_iso
        if date_to_iso:
            params["date_to"] = date_to_iso

        r = requests.get(API, params=params, timeout=timeout_sec)
        if r.status_code != 200:
            break

        payload = r.json()
        rows = payload.get("results", [])
        if not rows:
            break

        out.extend(rows)
        if len(out) >= limit:
            break

        meta = payload.get("meta", {})
        if page >= meta.get("pageCount", 1):
            break

        page += 1
        time.sleep(sleep_seconds)

    return out
