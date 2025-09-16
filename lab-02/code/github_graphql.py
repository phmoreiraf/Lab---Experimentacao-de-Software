# github_graphql.py
# -----------------------------------------------------------
# Coleta repositórios Java via GitHub GraphQL (top-N por stars),
# incluindo stargazerCount (popularidade), releases (atividade),
# datas (maturidade), linguagem principal e contadores de PRs/issues.
# -----------------------------------------------------------

import os
import time
import math
import logging
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# -----------------------------------------------------------
# Configuração básica
# -----------------------------------------------------------
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_GRAPHQL = os.getenv("GITHUB_GRAPHQL_URL", "https://api.github.com/graphql")

if not GITHUB_TOKEN:
    raise RuntimeError(
        "GITHUB_TOKEN não encontrado. Defina no .env ou no ambiente."
    )

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
    # Dica: Se quiser detalhar rate-limit no response, use também:
    # "GraphQL-Features": "graphql-explorer-rli",
}

# -----------------------------------------------------------
# Query GraphQL
# - Busca repositórios em Java ordenados por estrelas.
# - Traz métricas necessárias ao LAB02.
# -----------------------------------------------------------
SEARCH_QUERY = """
query ($pageSize: Int!, $afterCursor: String) {
  search(
    query: "language:Java sort:stars-desc",
    type: REPOSITORY,
    first: $pageSize,
    after: $afterCursor
  ) {
    repositoryCount
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
        createdAt
        updatedAt
        primaryLanguage { name }
        pullRequests(states: MERGED) { totalCount }
        releases { totalCount }
        issues: issues { totalCount }
        closedIssues: issues(states: CLOSED) { totalCount }
      }
    }
  }
}
"""

# -----------------------------------------------------------
# Funções utilitárias
# -----------------------------------------------------------
def _post_graphql(payload: Dict, session: Optional[requests.Session] = None) -> requests.Response:
    """Executa POST em /graphql com backoff simples e tratamento de erros transitórios."""
    max_retries = 5
    backoff = 2.0
    sess = session or requests.Session()

    for attempt in range(1, max_retries + 1):
        resp = sess.post(GITHUB_GRAPHQL, json=payload, headers=HEADERS, timeout=60)
        # 2xx
        if 200 <= resp.status_code < 300:
            # Também checar erros GraphQL (campo "errors")
            data = resp.json()
            if "errors" in data:
                # Se for rate limit ou abuso, tente backoff
                msg = str(data["errors"])
                if "rate limit" in msg.lower() or "abuse" in msg.lower():
                    time.sleep(backoff)
                    backoff *= 1.6
                    continue
                # Erro irrecuperável
                raise RuntimeError(f"Erro GraphQL: {data['errors']}")
            return resp

        # Se 4xx (exceto 403 rate-limit/abuse) não vale insistir muito
        if 400 <= resp.status_code < 500 and resp.status_code not in (403, 429):
            raise RuntimeError(
                f"Erro {resp.status_code} na API GraphQL: {resp.text}"
            )

        # Para 5xx, 403 (rate limit/abuse) e 429, aplicar backoff
        time.sleep(backoff)
        backoff *= 1.6

    # Última tentativa falhou
    resp.raise_for_status()
    return resp  # pragma: no cover


def _normalize_node(node: Dict) -> Dict:
    """Normaliza um nó de repositório para o formato que gravamos no CSV."""
    primary_lang = None
    if node.get("primaryLanguage") and isinstance(node["primaryLanguage"], dict):
        primary_lang = node["primaryLanguage"].get("name")

    return {
        "nameWithOwner": node.get("nameWithOwner"),
        "stargazerCount": node.get("stargazerCount"),
        "createdAt": node.get("createdAt"),
        "updatedAt": node.get("updatedAt"),
        "primaryLanguage": primary_lang,
        "mergedPRs": (node.get("pullRequests") or {}).get("totalCount", 0),
        "releases": (node.get("releases") or {}).get("totalCount", 0),
        "totalIssues": (node.get("issues") or {}).get("totalCount", 0),
        "closedIssues": (node.get("closedIssues") or {}).get("totalCount", 0),
    }


# -----------------------------------------------------------
# API pública
# -----------------------------------------------------------
def fetch_repositories(n_repos: int) -> List[Dict]:
    """
    Busca os top-N repositórios Java por estrelas usando GraphQL.
    Retorna uma lista de dicionários com campos prontos para salvar no CSV.
    """
    if n_repos < 1 or n_repos > 1000:
        raise ValueError("n_repos deve estar entre 1 e 1000 (limite da busca do GitHub).")

    results: List[Dict] = []
    after_cursor = None

    with requests.Session() as sess:
        while len(results) < n_repos:
            page_size = min(100, n_repos - len(results))
            payload = {
                "query": SEARCH_QUERY,
                "variables": {"pageSize": page_size, "afterCursor": after_cursor},
            }
            resp = _post_graphql(payload, sess)
            data = resp.json()
            search = data.get("data", {}).get("search", {})

            nodes = search.get("nodes", []) or []
            for node in nodes:
                repo = _normalize_node(node)
                # sanity: repositório precisa ter owner/name
                if repo["nameWithOwner"]:
                    results.append(repo)
                    if len(results) >= n_repos:
                        break

            page_info = search.get("pageInfo", {})
            has_next = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")

            # Segurança para evitar loop infinito (caso raro)
            if not has_next and len(results) < n_repos:
                logging.warning(
                    "Busca encerrou antes de atingir n_repos; retornando %d itens.",
                    len(results),
                )
                break

            # Respeitar a API
            time.sleep(0.7)

    return results
