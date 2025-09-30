import os
import time
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not found. Create a .env file (see .env.example).")

GQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

def _post_graphql(query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    for attempt in range(4):
        resp = requests.post(GQL_URL, headers=HEADERS, json={"query": query, "variables": variables}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if "errors" in data:
                # Backoff when hitting rate limit or transient errors
                time.sleep(2 + attempt * 2)
                continue
            return data["data"]
        # GitHub rate limit backoff
        time.sleep(2 + attempt * 2)
    raise RuntimeError(f"GraphQL request failed after retries. Last status={resp.status_code}, body={resp.text[:300]}")

def fetch_top_repositories(total: int = 200, min_closed_or_merged_prs: int = 100) -> List[Dict[str, Any]]:
    """Return top repos sorted by stars that also have >= min_closed_or_merged_prs PRs (MERGED + CLOSED)."""
    query = """
    query searchRepos($pageSize: Int!, $after: String) {
      search(query: "sort:stars", type: REPOSITORY, first: $pageSize, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          ... on Repository {
            nameWithOwner
            stargazerCount
            primaryLanguage { name }
            pullRequests(states:[MERGED, CLOSED]) { totalCount }
          }
        }
      }
    }
    """
    results: List[Dict[str, Any]] = []
    after = None
    page_size = 50
    while len(results) < total:
        data = _post_graphql(query, {"pageSize": page_size, "after": after})
        search = data["search"]
        for repo in search["nodes"]:
            if repo["pullRequests"]["totalCount"] >= min_closed_or_merged_prs:
                results.append(repo)
                if len(results) >= total:
                    break
        if not search["pageInfo"]["hasNextPage"]:
            break
        after = search["pageInfo"]["endCursor"]
        time.sleep(1)  # be polite with API
    return results[:total]

def fetch_pull_requests(name_with_owner: str, max_prs_per_repo: int = 500) -> List[Dict[str, Any]]:
    """Fetch MERGED or CLOSED PRs with at least one review, including metrics needed for the lab."""
    owner, name = name_with_owner.split("/")
    query = """
    query prs($owner: String!, $name: String!, $pageSize: Int!, $after: String) {
      repository(owner: $owner, name: $name) {
        pullRequests(states: [MERGED, CLOSED], orderBy: {field: CREATED_AT, direction: DESC}, first: $pageSize, after: $after) {
          pageInfo { hasNextPage endCursor }
          nodes {
            number
            state
            merged
            createdAt
            mergedAt
            closedAt
            body
            changedFiles
            additions
            deletions
            comments { totalCount }
            reviewThreads { totalCount }
            participants { totalCount }
            reviews(states: [APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED, PENDING]) { totalCount }
          }
        }
      }
    }
    """
    out: List[Dict[str, Any]] = []
    after = None
    page_size = 50
    while len(out) < max_prs_per_repo:
        data = _post_graphql(query, {"owner": owner, "name": name, "pageSize": page_size, "after": after})
        pr_page = data["repository"]["pullRequests"]
        for pr in pr_page["nodes"]:
            out.append(pr)
            if len(out) >= max_prs_per_repo:
                break
        if not pr_page["pageInfo"]["hasNextPage"]:
            break
        after = pr_page["pageInfo"]["endCursor"]
        time.sleep(0.5)
    return out
