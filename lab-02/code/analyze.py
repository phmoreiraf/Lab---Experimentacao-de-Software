import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ===== CONFIGURAÇÃO =====
backup_original_csv = "../data/raw_repos/resultados1000repos.csv"
ck_base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "ck_m")
charts_dir = os.path.join(os.path.dirname(__file__), "../charts")
os.makedirs(charts_dir, exist_ok=True)
metrics_path = os.path.join("../data", "final_metrics.txt")


# ===== FUNÇÕES AUXILIARES =====
def load_original_data(path):
    df = pd.read_csv(path)
    df["createdAt"] = pd.to_datetime(df["createdAt"]).dt.tz_localize(None)
    df["age_years"] = (datetime.now() - df["createdAt"]).dt.days // 365
    return df

def load_ck_data(repo_name):
    repo_dir = os.path.join(ck_base_dir, repo_name.replace("/", "_"), "ck_output")
    class_csv = os.path.join(repo_dir, "class.csv")
    if os.path.exists(class_csv):
        df_class = pd.read_csv(class_csv)
        if df_class.empty:
            return None
        return df_class
    return None

def aggregate_ck_metrics(df_class):
    return {
        "loc": df_class["loc"].sum(),
        "cbo_mean": df_class["cbo"].mean(),
        "dit_mean": df_class["dit"].mean(),
        "lcom_mean": df_class["lcom"].mean(),
    }

# ===== FUNÇÃO DE CONSOLIDAÇÃO =====
def consolidate_data(original_csv):
    df_original = load_original_data(original_csv)
    metrics = []
    valid_count = 0
    invalid_count = 0
    for _, row in df_original.iterrows():
        repo = row["nameWithOwner"]
        df_class = load_ck_data(repo)
        if df_class is None:
            print_and_write(content=f"[!] CK não encontrado para {repo}\n") 
            invalid_count += 1
            continue
        agg = aggregate_ck_metrics(df_class)
        agg["nameWithOwner"] = repo
        metrics.append(agg)
        valid_count += 1
    df_ck = pd.DataFrame(metrics)
    df_final = df_original.merge(df_ck, on="nameWithOwner")
    print_and_write(content=f"[+] CK encontrado para {valid_count} repositórios\n")
    print_and_write(content=f"[!] CK não encontrado para {invalid_count} repositórios\n")
    return df_final

# ===== FUNÇÕES PARA RQS =====
def analizar_rq01(df_final):
    """RQ01 - Popularidade x Qualidade"""
    print_and_write(content="\n=== RQ01 ===\n")

    # Correlações
    print_and_write(content=f"\nPearson:\n{df_final.corr(method='pearson')['stargazerCount']}\n")
    print_and_write(content=f"\nSpearman:\n{df_final.corr(method='spearman')['stargazerCount']}\n")

    # Gráficos

    # Popularidade vs LOC
    plt.scatter(df_final["stargazerCount"], df_final["loc"])
    plt.xlabel("Stars (popularidade)")
    plt.ylabel("LOC")
    title = "Popularidade vs LOC"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Popularidade vs CBO
    plt.scatter(df_final["stargazerCount"], df_final["cbo_mean"])
    plt.xlabel("Stars (popularidade)")
    plt.ylabel("CBO médio")
    title = "Popularidade vs CBO"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Popularidade vs DIT
    plt.scatter(df_final["stargazerCount"], df_final["dit_mean"])
    plt.xlabel("Stars (popularidade)")
    plt.ylabel("DIT médio")
    title = "Popularidade vs DIT"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Popularidade vs LCOM
    plt.scatter(df_final["stargazerCount"], df_final["lcom_mean"])
    plt.xlabel("Stars (popularidade)")
    plt.ylabel("LCOM médio")
    title = "Popularidade vs LCOM"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

def analizar_rq02(df_final):
    """RQ02 - Maturidade x Qualidade"""
    print_and_write(content="\n=== RQ02 ===\n")

    # Correlações com maturidade (idade)
    pearson_corr = df_final.corr(method="pearson")["age_years"]
    spearman_corr = df_final.corr(method="spearman")["age_years"]
    print_and_write(content=f"\nPearson:\n{pearson_corr}\n")
    print_and_write(content=f"\nSpearman:\n{spearman_corr}\n")

    # Gráficos individuais

    # Maturidade vs LOC
    plt.scatter(df_final["age_years"], df_final["loc"])
    plt.xlabel("Idade (anos)")
    plt.ylabel("LOC")
    title = "Maturidade vs LOC"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Maturidade vs CBO
    plt.scatter(df_final["age_years"], df_final["cbo_mean"])
    plt.xlabel("Idade (anos)")
    plt.ylabel("CBO médio")
    title = "Maturidade vs CBO"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Maturidade vs DIT
    plt.scatter(df_final["age_years"], df_final["dit_mean"])
    plt.xlabel("Idade (anos)")
    plt.ylabel("DIT médio")
    title = "Maturidade vs DIT"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Maturidade vs LCOM
    plt.scatter(df_final["age_years"], df_final["lcom_mean"])
    plt.xlabel("Idade (anos)")
    plt.ylabel("LCOM médio")
    title = "Maturidade vs LCOM"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

def analizar_rq03(df_final):
    """RQ03 - Atividade x Qualidade"""
    print_and_write(content="\n=== RQ03 ===\n")

    # Correlações com atividade (número de releases)
    pearson_corr = df_final.corr(method="pearson")["releases"]
    spearman_corr = df_final.corr(method="spearman")["releases"]
    print_and_write(content=f"\nPearson:\n{pearson_corr}\n")
    print_and_write(content=f"\nSpearman:\n{spearman_corr}\n")

    # Gráficos individuais

    # Atividade vs LOC
    plt.scatter(df_final["releases"], df_final["loc"])
    plt.xlabel("Número de releases (atividade)")
    plt.ylabel("LOC")
    title = "Atividade vs LOC"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Atividade vs CBO
    plt.scatter(df_final["releases"], df_final["cbo_mean"])
    plt.xlabel("Número de releases (atividade)")
    plt.ylabel("CBO médio")
    title = "Atividade vs CBO"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Atividade vs DIT
    plt.scatter(df_final["releases"], df_final["dit_mean"])
    plt.xlabel("Número de releases (atividade)")
    plt.ylabel("DIT médio")
    title = "Atividade vs DIT"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Atividade vs LCOM
    plt.scatter(df_final["releases"], df_final["lcom_mean"])
    plt.xlabel("Número de releases (atividade)")
    plt.ylabel("LCOM médio")
    title = "Atividade vs LCOM"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

def analizar_rq04(df_final):
    """RQ04 - Tamanho x Qualidade"""
    print_and_write(content="\n=== RQ04 ===\n")

    # Correlações com tamanho (LOC)
    pearson_corr = df_final.corr(method="pearson")["loc"]
    spearman_corr = df_final.corr(method="spearman")["loc"]
    print_and_write(content=f"\nPearson:\n{pearson_corr}\n")
    print_and_write(content=f"\nSpearman:\n{spearman_corr}\n")

    # Gráficos individuais

    # Tamanho vs CBO
    plt.scatter(df_final["loc"], df_final["cbo_mean"])
    plt.xlabel("LOC (tamanho)")
    plt.ylabel("CBO médio")
    title = "Tamanho vs CBO"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Tamanho vs DIT
    plt.scatter(df_final["loc"], df_final["dit_mean"])
    plt.xlabel("LOC (tamanho)")
    plt.ylabel("DIT médio")
    title = "Tamanho vs DIT"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()

    # Tamanho vs LCOM
    plt.scatter(df_final["loc"], df_final["lcom_mean"])
    plt.xlabel("LOC (tamanho)")
    plt.ylabel("LCOM médio")
    title = "Tamanho vs LCOM"
    plt.title(title)
    fname = title.replace(" ", "_") + ".png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()


def calc_stats(df_final):
    stats = df_final.describe().transpose()[["mean","50%","std"]]
    stats.rename(columns={"50%":"median"}, inplace=True)
    stats["mode"] = df_final.mode().iloc[0]
    print_and_write(content=f"{stats}\n")

# ===== FUNÇÃO PRINCIPAL DO PIPELINE =====
def run_analysis(original_csv=backup_original_csv):
    """
    Função que consolida os dados e chama todas as funções de RQ.
    """
    if os.path.exists(metrics_path):
        with open(metrics_path, "w") as f:
            f.write("")

    df_final = consolidate_data(original_csv)

    numeric_df = df_final.select_dtypes(include='number')
    calc_stats(numeric_df)
    analizar_rq01(numeric_df)
    analizar_rq02(numeric_df)
    analizar_rq03(numeric_df)
    analizar_rq04(numeric_df)

def print_and_write(file_path=metrics_path, content=""):
    with open(file_path, "a") as f:
        f.write(content)
    print(content)