import pandas as pd
import os
import concurrent.futures
import math

from github_graphql import fetch_repositories
from csv_controller import (save_to_csv, list_saved_results)
from ck_metrics_extractor import run_ck
from analyze import run_analysis

def print_main_menu():
    print("\nBem-vindo ao Lab 02!")
    print("1. Buscar dados dos repositórios Java")
    print("2. Rodar CK")
    print("3. Fazer análise estatística")
    print("4. Sair")
    option = input("Escolha uma opção: ").strip()
    return option

def choose_repos():
    raw_data = list_saved_results()
    if not raw_data:
        print("Nenhum resultado salvo encontrado. Busque repositórios primeiro.")
        return None
    print("Resultados salvos:")
    count = 1
    for file in raw_data:
        print(f"{count} - {file}")
        count += 1
    print("Escolha um arquivo para analisar ou '0' para voltar ao menu principal:")

    choice = input("Digite sua escolha: ").strip()
    if choice == "0":
        return None
    
    choice = int(choice)
    if choice not in range(1, count):
        print("Escolha inválida.")
        return None
        
    file_to_open = raw_data[choice - 1]
    data_path = f"../data/raw_repos/{file_to_open}"
    if not os.path.exists(data_path):
        print(f"Arquivo {data_path} não encontrado.")
        return None
    return data_path

if __name__ == '__main__':
    try:
        while(True):
            option = print_main_menu()
            print("\n")
            if(option == "1"):
                n_repos = int(input("Quantos repositórios deseja buscar? (Entre 10 e 1000) ").strip())
                if n_repos not in range(10, 1001):
                    print("Escolha inválida. Digite um número entre 10 e 1000.")
                    exit()

                print(f"Buscando dados dos {n_repos} repositórios Java mais populares...")
                repositorios = fetch_repositories(n_repos)
               
                save_to_csv(repositorios)
                print(f"Dados salvos em ../data/raw_repos/resultados{n_repos}Repos.csv")

            elif(option == "2"):
                data_path = choose_repos()
                if not data_path:
                    continue
                df = pd.read_csv(data_path)
                print(f"Rodando CK no arquivo {data_path}...")
                max_threads = 5

                def split_df(df, n_chunks):
                    chunk_size = math.ceil(len(df) / n_chunks)
                    return [df.iloc[i*chunk_size:(i+1)*chunk_size] for i in range(n_chunks)]

                df_chunks = split_df(df, max_threads)

                # Função wrapper para rodar cada chunk
                def process_chunk(chunk):
                    run_ck(chunk)

                with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                    futures = [executor.submit(process_chunk, chunk) for chunk in df_chunks]
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            future.result()  # lança exceções se houver
                        except Exception as e:
                            print(f"[ERRO] Um chunk falhou: {e}")
            
            elif(option == "3"):
                data_path = choose_repos()
                if not data_path:
                    continue
                run_analysis(data_path)

            else:
                print("Saindo...")
                exit()

    except Exception as e:
        print(f'Erro: {e}')
