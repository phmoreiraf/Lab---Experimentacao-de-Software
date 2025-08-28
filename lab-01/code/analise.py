import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def analisar_repositorios(data_path: str):
    if not os.path.exists(data_path):
        print(f"Arquivo {data_path} não encontrado.")
        return

    # Criação da pasta charts
    charts_dir = os.path.join(os.path.dirname(__file__), "../charts")
    os.makedirs(charts_dir, exist_ok=True)
    file_stem = os.path.splitext(os.path.basename(data_path))[0]
    metrics_path = os.path.join(charts_dir, f"metrics{file_stem}.txt")
    
    if(os.path.exists(metrics_path)):
        with open(metrics_path, "w") as f:
            f.write("")

    df = pd.read_csv(data_path)

    # Conversões de datas
    df["createdAt"] = pd.to_datetime(df["createdAt"]).dt.tz_localize(None)
    df["updatedAt"] = pd.to_datetime(df["updatedAt"]).dt.tz_localize(None)

    # Métricas adicionais
    df["idade_anos"] = (datetime.now() - df["createdAt"]).dt.days / 365
    df["idade_anos_round"] = df["idade_anos"].round(0)
    df["dias_desde_update"] = (datetime.now() - df["updatedAt"]).dt.days
    df["ratio_closed_issues"] = df["closedIssues"] / df["totalIssues"].replace(0, pd.NA)

    # =======================
    # Estatísticas RQ01 a RQ06
    # =======================
    print_and_write(metrics_path, "===== RQ01 - Idade dos repositorios (anos) =====\n")
    print_and_write(metrics_path, "Mediana: {}\n".format(round(df["idade_anos"].median(), 2)))
    print_and_write(metrics_path, "Media: {}\n".format(round(df["idade_anos"].mean(), 2)))
    print_and_write(metrics_path, "Moda: {}\n".format(round(df["idade_anos_round"].mode()[0], 2)))


    print_and_write(metrics_path, "===== RQ02 - Pull Requests Aceitos =====\n")
    print_and_write(metrics_path, "Mediana: {}\n".format(round(df["mergedPRs"].median(), 2)))
    print_and_write(metrics_path, "Media: {}\n".format(round(df["mergedPRs"].mean(), 2)))
    print_and_write(metrics_path, "Moda: {}\n".format(round(df["mergedPRs"].mode()[0], 2)))

    print_and_write(metrics_path, "===== RQ03 - Releases =====\n")
    print_and_write(metrics_path, "Mediana: {}\n".format(round(df["releases"].median(), 2)))
    print_and_write(metrics_path, "Media: {}\n".format(round(df["releases"].mean(), 2)))
    print_and_write(metrics_path, "Moda: {}\n".format(round(df["releases"].mode()[0], 2)))

    print_and_write(metrics_path, "===== RQ04 - Dias desde ultima atualizacao =====\n")
    print_and_write(metrics_path, "Mediana: {}\n".format(round(df["dias_desde_update"].median(), 2)))
    print_and_write(metrics_path, "Media: {}\n".format(round(df["dias_desde_update"].mean(), 2)))
    print_and_write(metrics_path, "Moda: {}\n".format(round(df["dias_desde_update"].mode()[0], 2)))

    print_and_write(metrics_path, "===== RQ05 - Linguagens mais usadas =====\n")
    print_and_write(metrics_path, "{}\n".format(df["primaryLanguage"].value_counts()))

    print_and_write(metrics_path, "===== RQ06 - Percentual de Issues Fechadas =====\n")
    print_and_write(metrics_path, "Mediana: {}\n".format(round(df["ratio_closed_issues"].median() * 100, 2)))
    print_and_write(metrics_path, "Media: {}\n".format(round(df["ratio_closed_issues"].mean() * 100, 2)))
    print_and_write(metrics_path, "Moda: {}\n".format(round(df["ratio_closed_issues"].mode()[0] * 100, 2)))

    # =======================
    # Gráficos principais
    # =======================
    # Idade dos repositórios

    df["idade_anos"].hist(bins=15)
    plt.title("Distribuição da Idade dos Repositórios (anos)")
    plt.xlabel("Idade (anos)")
    plt.ylabel("Quantidade")
    plt.savefig(os.path.join(charts_dir, f"idade_{file_stem}.png"))
    plt.close()

    # Pull Requests Aceitos
    df["mergedPRs"].dropna().hist(bins=30)
    plt.title("Distribuição Pull Requests Aceitos")
    plt.xlabel("Pull Requests Aceitos")
    plt.ylabel("Quantidade")
    plt.savefig(os.path.join(charts_dir, f"pull_requests_aceitos_{file_stem}.png"))
    plt.close()

    # Pull Requests Aceitos 90%
    s = df["mergedPRs"].dropna()
    limite = s.quantile(0.9)  # valor do percentil 90

    x = np.sort(s[s <= limite])
    y = np.arange(1, len(x)+1) / len(x)
    plt.plot(x, y, marker=".", linestyle="none")
    plt.title("ECDF de Pull Requests Aceitos (até o 90º percentil)")
    plt.xlabel("Pull Requests Aceitos")
    plt.ylabel("Proporção acumulada")
    plt.savefig(os.path.join(charts_dir, f"pull_requests_aceitos_ECDF_{file_stem}.png"))
    plt.close()

    # Top linguagens
    df["primaryLanguage"].value_counts().head(5).plot(kind="bar", figsize=(7, 8))
    plt.title("Top 5 Linguagens Mais Populares")
    plt.ylabel("Quantidade")
    plt.xlabel("Linguagem")
    plt.savefig(os.path.join(charts_dir, f"linguagens_{file_stem}.png"))
    plt.close()

    # Percentual de issues fechadas
    df["ratio_closed_issues"].dropna().hist(bins=15)
    plt.title("Distribuição da Razão de Issues Fechadas")
    plt.xlabel("Proporção")
    plt.ylabel("Quantidade")
    plt.savefig(os.path.join(charts_dir, f"issues_fechadas_{file_stem}.png"))
    plt.close()

    print(f"\nGráficos salvos em {charts_dir}")

    # =======================
    # Bônus RQ07 - Por linguagem
    # =======================
    print_and_write(metrics_path, "\n===== RQ07 - Metricas por Linguagem =====\n")
    linguagens_populares = df["primaryLanguage"].value_counts().head(5).index.tolist()
    print_and_write(metrics_path, "Linguagens mais populares: {}\n".format(linguagens_populares))

    df_populares = df[df["primaryLanguage"].isin(linguagens_populares)]
    df_outras = df[~df["primaryLanguage"].isin(linguagens_populares)]

    print_and_write(metrics_path, "\n--- Pull Requests Aceitos ---\n")
    print_and_write(metrics_path, "Populares: {}\n".format(df_populares["mergedPRs"].median()))
    print_and_write(metrics_path, "Outras: {}\n".format(df_outras["mergedPRs"].median()))

    print_and_write(metrics_path, "\n--- Releases ---\n")
    print_and_write(metrics_path, "Populares: {}\n".format(df_populares["releases"].median()))
    print_and_write(metrics_path, "Outras: {}\n".format(df_outras["releases"].median()))

    print_and_write(metrics_path, "\n--- Dias desde ultima atualizacao ---\n")
    print_and_write(metrics_path, "Populares: {}\n".format(df_populares["dias_desde_update"].median()))
    print_and_write(metrics_path, "Outras: {}\n".format(df_outras["dias_desde_update"].median()))


def print_and_write(file_path, content):
    with open(file_path, "a") as f:
        f.write(content)
    print(content)