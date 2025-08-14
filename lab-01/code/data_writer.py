import csv
import os

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
