import requests
import os
from dotenv import load_dotenv
 
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

token = GITHUB_TOKEN

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


def fetch_repositories(total_repos):
    results = []
    page_size = min(100, total_repos)  # GitHub limit per query
    after_cursor = None

    while len(results) < total_repos:
        variables = {
            "pageSize": page_size,
            "afterCursor": after_cursor
        }
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(f"Query failed: {response.status_code}, {response.text}")

        data = response.json()["data"]["search"]
        results.extend(data["nodes"])

        if not data["pageInfo"]["hasNextPage"]:
            break

        after_cursor = data["pageInfo"]["endCursor"]

        # Adjust the last page size if needed
        remaining = total_repos - len(results)
        page_size = min(100, remaining)

    return results[:total_repos]