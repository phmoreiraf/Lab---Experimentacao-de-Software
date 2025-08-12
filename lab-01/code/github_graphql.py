import csv
import os
import time

import requests
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    raise Exception("Erro: GITHUB_TOKEN não encontrado no arquivo .env")

query = """
query ($pageSize: Int!, $afterCursor: String) {
  search(query: "stars:>1 sort:stars", type: REPOSITORY, first: $pageSize, after: $afterCursor) {
    nodes {
      ... on Repository {
        nameWithOwner
        createdAt
        updatedAt
        primaryLanguage { name }
        pullRequests(states: MERGED) { totalCount }
        releases { totalCount }
        issues { totalCount }
        closedIssues: issues(states: CLOSED) { totalCount }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}


def fetch_repositories(total_repos=100):
    results = []
    page_size = min(100, total_repos)
    after_cursor = None

    while len(results) < total_repos:
        variables = {
            "pageSize": page_size,
            "afterCursor": after_cursor
        }

        # Tentativa com retry automático
        for tentativa in range(3):
            try:
                response = requests.post(
                    "https://api.github.com/graphql",
                    json={"query": query, "variables": variables},
                    headers=headers,
                    timeout=15  # evita travar indefinidamente
                )

                if response.status_code == 200:
                    break
                else:
                    print(f"[AVISO] Falha {response.status_code}, tentativa {tentativa+1}/3")
                    print(f"[DEBUG] Conteúdo da resposta: {response.text}")
                    time.sleep(5)

            except requests.exceptions.RequestException as e:
                print(f"[ERRO] Problema de conexão: {e}, tentativa {tentativa+1}/3")
                time.sleep(5)
        else:
            print(f"[ERRO] Query falhou após 3 tentativas. Última resposta:")
            print(f"Status: {response.status_code}")
            print(f"Headers: {response.headers}")
            print(f"Body: {response.text}")
            raise Exception(f"Query falhou após 3 tentativas: {response.status_code}, {response.text}")

        try:
            data = response.json().get("data", {}).get("search", None)
        except Exception as e:
            print(f"[ERRO] Falha ao decodificar JSON da resposta: {e}")
            print(f"Resposta bruta: {response.text}")
            raise
        if not data:
            print(f"[ERRO] Resposta inesperada da API:")
            print(f"Status: {response.status_code}")
            print(f"Headers: {response.headers}")
            print(f"Body: {response.text}")
            raise Exception(f"Resposta inesperada da API: {response.text}")

        results.extend(data["nodes"])

        if not data["pageInfo"]["hasNextPage"]:
            break

        after_cursor = data["pageInfo"]["endCursor"]
        remaining = total_repos - len(results)
        page_size = min(100, remaining)

        time.sleep(1)  # evita sobrecarregar a API

    save_to_csv(results)
    return results[:total_repos]


def save_to_csv(repositories):
    # Salva no diretório ../data
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "resultados100Repos.csv")

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "nameWithOwner", "createdAt", "updatedAt",
            "primaryLanguage", "mergedPRs", "releases",
            "totalIssues", "closedIssues"
        ])
        for repo in repositories:
            writer.writerow([
                repo['nameWithOwner'],
                repo['createdAt'],
                repo['updatedAt'],
                repo['primaryLanguage']['name'] if repo['primaryLanguage'] else None,
                repo['pullRequests']['totalCount'],
                repo['releases']['totalCount'],
                repo['issues']['totalCount'],
                repo['closedIssues']['totalCount']
            ])
