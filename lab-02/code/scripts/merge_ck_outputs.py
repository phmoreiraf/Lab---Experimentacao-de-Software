#!/usr/bin/env python
import os, glob, pandas as pd

RAW = "data/metrics_raw"
OUT = "data/metrics_merged.csv"

def add_repo_id(df, repo_id):
    df["repo_id"] = repo_id
    return df

def main():
    os.makedirs("data", exist_ok=True)
    frames = []
    for repo_dir in glob.glob(os.path.join(RAW, "*")):
        repo_id = os.path.basename(repo_dir)
        for csv_path in glob.glob(os.path.join(repo_dir, "*.csv")):
            try:
                df = pd.read_csv(csv_path)
                # normaliza colunas comuns
                cols = {c.lower(): c for c in df.columns}
                if "file" in df.columns: df.rename(columns={"file": "source_file"}, inplace=True)
                df = add_repo_id(df, repo_id)
                frames.append(df)
            except Exception as e:
                print(f"[WARN] Falha ao ler {csv_path}: {e}")

    if not frames:
        raise SystemExit("Nenhum CSV do CK encontrado em data/metrics_raw/.")

    big = pd.concat(frames, ignore_index=True)
    big.to_csv(OUT, index=False)
    print(f"[OK] {OUT} com {len(big)} linhas")

if __name__ == "__main__":
    main()