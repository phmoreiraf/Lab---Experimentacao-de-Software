import argparse, os, pandas as pd
from dataset import build_repos_list, build_prs_dataset, RAW_DIR, PROC_DIR
from analysis_rqs import run_all

def print_main_menu():
    print("\nBem-vindo ao buscador de PRs do GitHub!")
    print("1. Buscar dados dos repositórios mais populares")
    print("2. Buscar PRs")
    print("3. Analisar dados dos PRs")
    print("4. Sair")
    option = input("Escolha uma opção: ").strip()
    return option

def main():
    try:
        while(True):
            option = print_main_menu()
            print("\n")
            if(option == "1"):
                n_repos = int(input("Quantos repositórios deseja buscar? (Entre 10 e 200) ").strip())
                if n_repos not in range(10, 201):
                    print("Escolha inválida. Digite um número entre 10 e 200.")
                    continue
                print(f"Buscando dados dos {n_repos} repositórios mais populares...")
                repositorios = build_repos_list(n=n_repos, min_prs=100, save_csv=True)
                print(f"[!] Dados salvos em ../data/raw/repos_top{n_repos}_min100PRs.csv")

            elif(option == "2"):
                repo_file = input(f"Digite o nome do arquivo CSV na pasta {RAW_DIR} (ex: repos_top50_min100PRs.csv): ").strip()
                if not os.path.isfile(os.path.join(RAW_DIR, repo_file)):
                    print(f"[X] Arquivo {repo_file} não encontrado na pasta {RAW_DIR}.")
                    continue
                try:
                    repos_df = pd.read_csv(os.path.join(RAW_DIR, repo_file))
                except Exception as e:
                    print(f"[X] Erro ao ler o arquivo {repo_file}: {e}")
                    continue

                max_prs = int(input("Quantos PRs por repositório deseja buscar? (Entre 10 e 500) ").strip())
                if max_prs not in range(10, 501):
                    print("[X] Escolha inválida. Digite um número entre 10 e 500.")
                    continue

                print(f"Buscando até {max_prs} PRs por repositório...")
                prs_df = build_prs_dataset(repos_df, max_prs_per_repo=max_prs, save_intermediate=True)
                
                print(f"[!] Dados salvos em {os.path.join(PROC_DIR, 'dataset_prs.csv')}")
                
            elif(option == "3"):
                print("Analisando dados dos PRs...")
                run_all()
                print(f"[!] Resultados salvos em {os.path.join(PROC_DIR, 'metrics_report.txt')} e na pasta ../charts")
            else:
                print("Saindo...")
                exit()

    except Exception as e:
        print(f'Erro: {e}')

if __name__ == "__main__":
    main()
