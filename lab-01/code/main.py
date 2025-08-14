from github_graphql import fetch_repositories
from data_writer import save_to_csv

if __name__ == '__main__':
    try:
        escolha = int(input("Quantos repositórios deseja buscar? ").strip())
        if escolha not in range(10, 1001):
            print("Escolha inválida. Digite um número entre 10 e 1000.")
            exit()

        print(f"Buscando dados dos {escolha} repositórios mais populares...")
        repositorios = fetch_repositories(escolha)
        save_to_csv(repositorios)
        print(f"Dados salvos em ../data/resultados{escolha}Repos.csv")

    except Exception as e:
        print(f'Erro: {e}')
