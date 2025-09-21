import csv
import os

data_dir = os.path.join(os.path.dirname(__file__), "../data/raw_repos")

def save_to_csv(repositories):
    # Salva no diretório ../data
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"resultados{len(repositories)}Repos.csv")

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "nameWithOwner", "createdAt", "releases",
            "stargazerCount", "defaultBranchRef"
        ])
        for repo in repositories:
            writer.writerow([
                repo['nameWithOwner'],
                repo['createdAt'],
                repo['releases']['totalCount'],
                repo['stargazerCount'],
                repo['defaultBranchRef']['name'] if repo['defaultBranchRef'] else 'main'
            ])

def list_saved_results():
    files = os.listdir(data_dir)
    csv_files = [f for f in files if f.endswith(".csv")]
    return csv_files