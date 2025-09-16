from github_graphql import fetch_repositories
from csv_controller import save_to_csv, list_saved_results
from analise import analisar_repositorios

import os
import subprocess
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def print_main_menu():
    print("\nBem-vindo ao buscador de repositórios do GitHub!")
    print("1. Buscar dados dos repositórios mais populares (GraphQL)")
    print("2. Analisar CSV salvo (gráficos exploratórios)")
    print("3. Pipeline CK + RQ1–RQ4 (clonar, medir, unificar, sumarizar, correlações, figuras)")
    print("4. Apenas gerar relatório (usa CSVs existentes em data/)")
    print("5. Sair")
    option = input("Escolha uma opção: ").strip()
    return option

def run_make(target, top=None):
    env = os.environ.copy()
    if top:
        env["TOP"] = str(top)
    cmd = ["make", target]
    print(f"[RUN] {' '.join(cmd)}  (TOP={env.get('TOP','(padrão)')})")
    proc = subprocess.run(cmd, env=env)
    if proc.returncode != 0:
        print(f"[ERRO] Falha em make {target}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        while True:
            option = print_main_menu()
            print()
            if option == "1":
                n_repos = int(input("Quantos repositórios deseja buscar? (10 a 1000) ").strip())
                if n_repos not in range(10, 1001):
                    print("Escolha inválida. Digite um número entre 10 e 1000.")
                    continue
                print(f"Buscando dados dos {n_repos} repositórios mais populares...")
                repositorios = fetch_repositories(n_repos)
                save_to_csv(repositorios)
                print(f"Dados salvos em data/resultados{n_repos}Repos.csv e/ou data/repos.csv (via make fetch).")

            elif option == "2":
                raw_data = list_saved_results()
                if not raw_data:
                    print("Nenhum CSV encontrado em data/. Busque repositórios primeiro.")
                    continue
                print("Resultados salvos:")
                for idx, file in enumerate(raw_data, start=1):
                    print(f"{idx} - {file}")
                print("Escolha um arquivo para analisar ou '0' p/ voltar:")
                choice = input("Digite sua escolha: ").strip()
                if choice == "0":
                    continue
                try:
                    choice = int(choice)
                    if choice not in range(1, len(raw_data) + 1):
                        raise ValueError
                    file_to_open = raw_data[choice - 1]
                    analisar_repositorios(os.path.join("data", file_to_open))
                except ValueError:
                    print("Escolha inválida.")

            elif option == "3":
                top = input("TOP (padrão 1000) [Enter p/ padrão]: ").strip() or None
                # pipeline completa com Makefile
                run_make("all", top)
                print("Pipeline CK + RQ1–RQ4 concluída. Veja data/ e reports/.")

            elif option == "4":
                run_make("report")
                print("Relatório (reports/report.md) gerado a partir de CSVs existentes.")

            elif option == "5":
                print("Saindo...")
                sys.exit(0)
            else:
                print("Opção inválida.")

    except Exception as e:
        print(f'Erro: {e}')
