import os
from typing import Any, Dict, List

import pandas as pd
from gh_api import fetch_pull_requests, fetch_top_repositories

# Pastas de saída
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROC_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

def _end_time(pr: Dict[str, Any]):
    return pr.get("mergedAt") or pr.get("closedAt")

def build_repos_list(n: int = 200, min_prs: int = 100, save_csv: bool = True) -> pd.DataFrame:
    repos = fetch_top_repositories(total=n, min_closed_or_merged_prs=min_prs)
    df = pd.DataFrame(repos)
    if save_csv:
        df.to_csv(os.path.join(RAW_DIR, f"repos_top{n}_min{min_prs}PRs.csv"), index=False)
    return df

def build_prs_dataset(repos_df: pd.DataFrame, max_prs_per_repo: int = 500, save_intermediate: bool = True) -> pd.DataFrame:
    rows: List[pd.DataFrame] = []
    for _, r in repos_df.iterrows():
        repo = r["nameWithOwner"]
        prs = fetch_pull_requests(repo, max_prs_per_repo=max_prs_per_repo)
        pr_df = pd.DataFrame(prs)
        if pr_df.empty:
            continue

        # Campos derivados
        pr_df["repo"] = repo
        pr_df["endTime"] = pr_df["mergedAt"].fillna(pr_df["closedAt"])
        pr_df["createdAt"] = pd.to_datetime(pr_df["createdAt"], utc=True)
        pr_df["endTime"] = pd.to_datetime(pr_df["endTime"], utc=True)
        pr_df = pr_df[~pr_df["endTime"].isna()]

        # Filtros do enunciado
        # (1) MERGED ou CLOSED -> já vem da query
        # (2) Pelo menos 1 review
        pr_df = pr_df[pr_df["reviews"].apply(lambda x: (x or {}).get("totalCount", 0)) >= 1]
        # (3) Duração >= 1 hora
        pr_df["analysis_hours"] = (pr_df["endTime"] - pr_df["createdAt"]).dt.total_seconds() / 3600.0
        pr_df = pr_df[pr_df["analysis_hours"] >= 1.0]

        # Métricas
        pr_df["size_files"] = pr_df["changedFiles"].fillna(0).astype(int)
        pr_df["size_additions"] = pr_df["additions"].fillna(0).astype(int)
        pr_df["size_deletions"] = pr_df["deletions"].fillna(0).astype(int)
        pr_df["desc_len_chars"] = pr_df["body"].fillna("").astype(str).str.len()

        pr_df["interactions_participants"] = pr_df["participants"].apply(
            lambda x: (x or {}).get("totalCount", 0)
        ).astype(int)

        # Separar contagens de comentários conforme interpretação mais fiel ao enunciado
        pr_df["interactions_comments_issue"] = pr_df["comments"].apply(
            lambda x: (x or {}).get("totalCount", 0)
        ).astype(int)
        pr_df["interactions_review_threads"] = pr_df["reviewThreads"].apply(
            lambda x: (x or {}).get("totalCount", 0)
        ).astype(int)
        pr_df["interactions_comments"] = pr_df["interactions_comments_issue"] + pr_df["interactions_review_threads"]

        pr_df["reviews_count"] = pr_df["reviews"].apply(lambda x: (x or {}).get("totalCount", 0)).astype(int)

        pr_df["final_status"] = pr_df.apply(lambda row: "MERGED" if bool(row.get("merged")) else "CLOSED", axis=1)
        pr_df["final_status_bin"] = (pr_df["final_status"] == "MERGED").astype(int)

        keep_cols = [
            "repo","number","final_status","final_status_bin","analysis_hours",
            "size_files","size_additions","size_deletions","desc_len_chars",
            "interactions_participants","interactions_comments_issue","interactions_review_threads",
            "interactions_comments","reviews_count","createdAt","endTime","state","merged"
        ]
        pr_df = pr_df[keep_cols]

        if save_intermediate:
            out_repo_csv = os.path.join(RAW_DIR, f"prs_{repo.replace('/', '_')}.csv")
            pr_df.to_csv(out_repo_csv, index=False)

        rows.append(pr_df)

    if not rows:
        return pd.DataFrame()

    full = pd.concat(rows, ignore_index=True)
    # Salva dataset processado
    full.to_csv(os.path.join(PROC_DIR, "dataset_prs.csv"), index=False)
    try:
        full.to_parquet(os.path.join(PROC_DIR, "dataset_prs.parquet"))
    except Exception:
        pass
    return full
