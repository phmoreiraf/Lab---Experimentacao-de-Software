from github_graphql import fetch_repositories

# Dependencias: requests, numpy, matplotlib e pandas

def ratio_issues_closed(total_issues, closed_issues):
    return closed_issues / total_issues if total_issues > 0 else 0

def print_results(repositories):
    for repo in repositories:
        total_issues = repo['issues']['totalCount']
        closed_issues = repo['closedIssues']['totalCount']
        print(f"Repository: {repo['nameWithOwner']}")
        print(f"  Created at: {repo['createdAt']}")
        print(f"  Last updated: {repo['updatedAt']}")
        print(f"  Primary language: {repo['primaryLanguage']['name'] if repo['primaryLanguage'] else 'None'}")
        print(f"  Merged Pull Requests: {repo['pullRequests']['totalCount']}")
        print(f"  Releases: {repo['releases']['totalCount']}")
        print(f"  Total Issues: {total_issues}")
        print(f"  Closed Issues: {closed_issues}")
        print(f"  Ratio of closed issues: {(ratio_issues_closed(total_issues, closed_issues) * 100):.2f}%")
        print("-" * 50)
    print("Total repositories fetched:", len(repositories))

# Main
if __name__ == '__main__':

    try:
        repositories = fetch_repositories(10)  # Fetch 10 repositories
        print_results(repositories)
    except Exception as e:
        print(f'Erro: {e}')