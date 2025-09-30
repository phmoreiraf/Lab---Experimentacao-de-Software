import argparse, os, pandas as pd
from dataset import build_repos_list, build_prs_dataset, RAW_DIR, PROC_DIR
from analysis_rqs import run_all

def main():
    parser = argparse.ArgumentParser(description="LAB-03: Code Review characterization on GitHub (PRs).")
    sub = parser.add_subparsers(dest="cmd")

    s1 = sub.add_parser("fetch-repos", help="Fetch top repositories by stars that have at least MIN_PRs (MERGED+CLOSED).")
    s1.add_argument("--n", type=int, default=200, help="How many repositories (default=200)")
    s1.add_argument("--min-prs", type=int, default=100, help="Minimum PRs merged+closed (default=100)")

    s2 = sub.add_parser("fetch-prs", help="Fetch PRs for repositories CSV and build processed dataset.")
    s2.add_argument("--repos-csv", type=str, default=None, help="CSV from fetch-repos; if omitted, uses the latest in data/raw")
    s2.add_argument("--max-per-repo", type=int, default=500, help="Max PRs per repo to fetch (default=500)")

    s3 = sub.add_parser("analyze", help="Run all RQs, compute correlations and export charts/report.")
    s3.add_argument("--dataset", type=str, default=None, help="Path to processed dataset (default uses data/processed/dataset_prs.csv)")

    args = parser.parse_args()

    if args.cmd == "fetch-repos":
        df = build_repos_list(n=args.n, min_prs=args.min_prs, save_csv=True)
        print(f"[OK] Saved repos CSV with {len(df)} rows in {RAW_DIR}")
    elif args.cmd == "fetch-prs":
        csv_path = args.repos_csv
        if not csv_path:
            # find latest repos csv in RAW_DIR
            candidates = [f for f in os.listdir(RAW_DIR) if f.startswith("repos_top") and f.endswith(".csv")]
            csv_path = os.path.join(RAW_DIR, sorted(candidates)[-1]) if candidates else None
        if not csv_path or not os.path.exists(csv_path):
            raise SystemExit("Repos CSV not found. Run 'python -m code.main fetch-repos' first or pass --repos-csv.")
        repos_df = pd.read_csv(csv_path)
        df = build_prs_dataset(repos_df, max_prs_per_repo=args.max_per_repo, save_intermediate=True)
        print(f"[OK] Processed dataset size: {len(df)} rows. Saved to {PROC_DIR}.")
    elif args.cmd == "analyze":
        run_all(args.dataset)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
