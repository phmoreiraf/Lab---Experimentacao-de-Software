from github_graphql import fetch_repositories

if __name__ == '__main__':
    try:
        escolha = input("Quantos repositórios deseja buscar? (100 ou 1000): ").strip()
        if escolha not in ["100", "1000"]:
            print("Escolha inválida. Digite 100 ou 1000.")
            exit()

        quantidade = int(escolha)
        print(f"Buscando dados dos {quantidade} repositórios mais populares...")
        fetch_repositories(quantidade)
        print(f"Dados salvos em ../data/resultados{quantidade}Repos.csv")

    except Exception as e:
        print(f'Erro: {e}')
