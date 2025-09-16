# main.py
import os
import subprocess
import sys
from glob import glob

from analise import analisar_repositorios
from csv_controller import list_saved_results, save_to_csv
from github_graphql import fetch_repositories

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

def print_main_menu():
    print("\n=== LAB02 • Qualidade em Sistemas Java ===")
    print("1. Buscar repositórios (GraphQL) e salvar CSV")
    print("2. Análise exploratória (gera TODOS os gráficos em charts/)")
    print("3. Pipeline completa CK + RQ1–RQ4 (gera figuras em data/figures/)")
    print("4. Apenas gerar relatório (reports/report.md)")
    print("5. Sair")
    return input("Escolha: ").strip()

def run(cmd, env=None):
    print(f"[RUN] {cmd}")
    rc = subprocess.call(cmd, shell=True, env=env or os.environ.copy())
    if rc != 0:
        print(f"[ERRO] Comando falhou (rc={rc}): {cmd}")
        sys.exit(rc)

def pick_latest_csv_in_data() -> str:
    # prioriza data/repos.csv; senão, pega o resultadosNRepos.csv mais recente
    repos = os.path.join(DATA_DIR, "repos.csv")
    if os.path.exists(repos):
        return repos
    candidates = sorted(glob(os.path.join(DATA_DIR, "resultados*Repos.csv")))
    if not candidates:
        raise FileNotFoundError("Nenhum CSV em data/. Rode a opção 1 primeiro.")
    return candidates[-1]

if __name__ == '__main__':
    try:
        while True:
            opt = print_main_menu()
            if opt == "1":
                n = int(input("Quantos repositórios (10–1000)? ").strip())
                if n < 10 or n > 1000:
                    print("Valor inválido.")
                    continue
                print(f"Coletando top-{n} repositórios Java...")
                data = fetch_repositories(n)
                path = save_to_csv(data)   # grava resultadosNRepos.csv e repos.csv
                print(f"[OK] CSV salvo: {path} e data/repos.csv")

            elif opt == "2":
                # Gera TODOS os gráficos exploratórios com base no melhor CSV disponível
                csv_path = pick_latest_csv_in_data()
                print(f"[INFO] Explorando {csv_path} -> charts/")
                analisar_repositorios(csv_path, auto_save=True, charts_dir=CHARTS_DIR)
                print("[OK] Gráficos exploratórios em charts/")

            elif opt == "3":
                # Pipeline completa: fetch (já temos CSV? opcional), measure, merge, process, summarize, analyze, report
                top = input("TOP (Enter = 1000): ").strip() or "1000"
                env = os.environ.copy()
                env["TOP"] = top
                # Se você quiser recusar refetch caso já exista repos.csv, comente a próxima linha:
                run("make fetch", env=env)
                run("make measure", env=env)
                run("make merge", env=env)
                run("make process", env=env)
                run("make summarize", env=env)
                # analyze agora SEMPRE gera gráficos e CSVs por par
                run("make analyze", env=env)
                run("make report", env=env)
                print("[OK] Pipeline completa. Verifique data/ e reports/.")

            elif opt == "4":
                run("make report")
                print("[OK] Relatório em reports/report.md")

            elif opt == "5":
                print("Saindo...")
                sys.exit(0)
            else:
                print("Opção inválida.")
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)
