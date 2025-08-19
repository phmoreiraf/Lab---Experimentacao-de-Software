from github_graphql import fetch_repositories
from csv_controller import (save_to_csv, list_saved_results)
from analise import analisar_repositorios

def print_main_menu():
    print("\nBem-vindo ao buscador de repositórios do GitHub!")
    print("1. Buscar dados dos repositórios mais populares")
    print("2. Analisar dados")
    print("3. Sair")
    option = input("Escolha uma opção: ").strip()
    return option

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

                print(f"Buscando dados dos {n_repos} repositórios mais populares...")
                repositorios = fetch_repositories(n_repos)
                save_to_csv(repositorios)
                print(f"Dados salvos em ../data/resultados{n_repos}Repos.csv")

            elif(option == "2"):
                raw_data = list_saved_results()
                if not raw_data:
                    print("Nenhum resultado salvo encontrado. Busque repositórios primeiro.")
                    continue
                print("Resultados salvos:")
                count = 1
                for file in raw_data:
                    print(f"{count} - {file}")
                    count += 1
                print("Escolha um arquivo para analisar ou '0' para voltar ao menu principal:")

                choice = input("Digite sua escolha: ").strip()
                if choice == "0":
                    continue
                try:
                    choice = int(choice)
                    if choice not in range(1, count):
                        raise ValueError
                    file_to_open = raw_data[choice - 1]
                    analisar_repositorios(f"../data/{file_to_open}")

                except ValueError:
                    print("Escolha inválida.")
                    continue

            else:
                print("Saindo...")
                exit()

    except Exception as e:
        print(f'Erro: {e}')
