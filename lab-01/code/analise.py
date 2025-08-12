import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

# Escolher qual arquivo analisar
escolha = input("Analisar dados de 100 ou 1000 repositórios? ").strip()
if escolha not in ["100", "1000"]:
    print("Escolha inválida. Digite 100 ou 1000.")
    exit()

data_path = os.path.join(os.path.dirname(__file__), f"../data/resultados{escolha}Repos.csv")
charts_dir = os.path.join(os.path.dirname(__file__), "../charts")
os.makedirs(charts_dir, exist_ok=True)

if not os.path.exists(data_path):
    print(f"Arquivo {data_path} não encontrado. Execute o main.py primeiro para gerar os dados.")
    exit()

df = pd.read_csv(data_path)

# Conversões de datas
df["createdAt"] = pd.to_datetime(df["createdAt"])
df["updatedAt"] = pd.to_datetime(df["updatedAt"])

# Métricas adicionais
df["idade_anos"] = (datetime.now() - df["createdAt"]).dt.days / 365
df["dias_desde_update"] = (datetime.now() - df["updatedAt"]).dt.days
df["ratio_closed_issues"] = df["closedIssues"] / df["totalIssues"].replace(0, pd.NA)

# =======================
# Estatísticas RQ01 a RQ06
# =======================
print("\n===== RQ01 - Idade dos repositórios (anos) =====")
print("Mediana:", round(df["idade_anos"].median(), 2))

print("\n===== RQ02 - Pull Requests Aceitos =====")
print("Mediana:", df["mergedPRs"].median())

print("\n===== RQ03 - Releases =====")
print("Mediana:", df["releases"].median())

print("\n===== RQ04 - Dias desde última atualização =====")
print("Mediana:", df["dias_desde_update"].median())

print("\n===== RQ05 - Linguagens mais usadas =====")
print(df["primaryLanguage"].value_counts())

print("\n===== RQ06 - Percentual de Issues Fechadas =====")
print("Mediana:", round(df["ratio_closed_issues"].median() * 100, 2), "%")

# =======================
# Gráficos principais
# =======================

# Idade dos repositórios
df["idade_anos"].hist(bins=30)
plt.title("Distribuição da Idade dos Repositórios (anos)")
plt.xlabel("Idade (anos)")
plt.ylabel("Quantidade")
plt.savefig(os.path.join(charts_dir, f"idade_{escolha}.png"))
plt.close()

# Top linguagens
df["primaryLanguage"].value_counts().head(10).plot(kind="bar")
plt.title("Top 10 Linguagens Mais Usadas")
plt.ylabel("Quantidade")
plt.savefig(os.path.join(charts_dir, f"linguagens_{escolha}.png"))
plt.close()

# Percentual de issues fechadas
df["ratio_closed_issues"].dropna().hist(bins=30)
plt.title("Distribuição da Razão de Issues Fechadas")
plt.xlabel("Proporção")
plt.ylabel("Quantidade")
plt.savefig(os.path.join(charts_dir, f"issues_fechadas_{escolha}.png"))
plt.close()

print(f"\nGráficos salvos em {charts_dir}")

# =======================
# Bônus RQ07 - Por linguagem
# =======================
print("\n===== RQ07 - Métricas por Linguagem =====")
linguagens_populares = df["primaryLanguage"].value_counts().head(5).index.tolist()
print(f"Linguagens mais populares: {linguagens_populares}")

df_populares = df[df["primaryLanguage"].isin(linguagens_populares)]
df_outras = df[~df["primaryLanguage"].isin(linguagens_populares)]

print("\n--- Pull Requests Aceitos ---")
print("Populares:", df_populares["mergedPRs"].median())
print("Outras:", df_outras["mergedPRs"].median())

print("\n--- Releases ---")
print("Populares:", df_populares["releases"].median())
print("Outras:", df_outras["releases"].median())

print("\n--- Dias desde última atualização ---")
print("Populares:", df_populares["dias_desde_update"].median())
print("Outras:", df_outras["dias_desde_update"].median())
