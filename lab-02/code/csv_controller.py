# csv_controller.py
# -----------------------------------------------------------
# Utilitários para salvar CSVs de repositórios e listar resultados.
# Agora inclui a coluna 'stargazerCount' (popularidade).
# -----------------------------------------------------------

import os
import csv
from typing import Dict, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Nome canônico (usado pela pipeline do LAB02)
CANONICAL_NAME = "repos.csv"

def _sanitize_int(value):
    try:
        return int(value)
    except Exception:
        return 0

def save_to_csv(repositories: List[Dict], also_canonical: bool = True) -> str:
    """
    Salva a lista de repositórios em:
      - data/resultados{N}Repos.csv (onde N = quantidade de registros)
      - opcionalmente também em data/repos.csv (nome canônico da pipeline)

    Retorna o caminho do arquivo específico salvo (resultados{N}Repos.csv).
    """
    if not repositories:
        raise ValueError("Lista de repositórios vazia.")

    n = len(repositories)
    specific_name = f"resultados{n}Repos.csv"
    specific_path = os.path.join(DATA_DIR, specific_name)

    # Cabeçalho padronizado (inclui stargazerCount)
    header = [
        "nameWithOwner",
        "stargazerCount",
        "createdAt",
        "updatedAt",
        "primaryLanguage",
        "mergedPRs",
        "releases",
        "totalIssues",
        "closedIssues",
    ]

    # Grava arquivo específico
    with open(specific_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for repo in repositories:
            w.writerow([
                repo.get("nameWithOwner"),
                _sanitize_int(repo.get("stargazerCount")),
                repo.get("createdAt"),
                repo.get("updatedAt"),
                repo.get("primaryLanguage"),
                _sanitize_int(repo.get("mergedPRs")),
                _sanitize_int(repo.get("releases")),
                _sanitize_int(repo.get("totalIssues")),
                _sanitize_int(repo.get("closedIssues")),
            ])

    # Grava o canônico data/repos.csv (utilizado pelos próximos estágios da pipeline)
    if also_canonical:
        canonical_path = os.path.join(DATA_DIR, CANONICAL_NAME)
        with open(canonical_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            for repo in repositories:
                w.writerow([
                    repo.get("nameWithOwner"),
                    _sanitize_int(repo.get("stargazerCount")),
                    repo.get("createdAt"),
                    repo.get("updatedAt"),
                    repo.get("primaryLanguage"),
                    _sanitize_int(repo.get("mergedPRs")),
                    _sanitize_int(repo.get("releases")),
                    _sanitize_int(repo.get("totalIssues")),
                    _sanitize_int(repo.get("closedIssues")),
                ])

    return specific_path


def list_saved_results() -> List[str]:
    """
    Lista arquivos CSV em data/ que o usuário pode escolher para análises exploratórias.
    Retorna nomes relativos à pasta data/ (por exemplo, 'resultados100Repos.csv').
    """
    files = []
    if not os.path.isdir(DATA_DIR):
        return files

    for name in os.listdir(DATA_DIR):
        if not name.lower().endswith(".csv"):
            continue
        # Mostramos tanto o canônico (repos.csv) quanto os específicos (resultadosNRepos.csv)
        if name == "repos.csv" or name.startswith("resultados"):
            files.append(name)

    # Ordena deixando repos.csv no topo e depois em ordem "natural" por N
    def _key(nm: str):
        if nm == "repos.csv":
            return (0, 0)
        # tentar extrair N de resultados{N}Repos.csv
        # fallback para comparar por nome
        try:
            middle = nm.replace("resultados", "").replace("Repos.csv", "")
            return (1, int(middle))
        except Exception:
            return (2, nm)

    return sorted(files, key=_key)
