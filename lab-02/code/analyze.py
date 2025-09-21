import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ===== CONFIGURAÇÃO =====
backup_original_csv = "../data/raw_repos/resultados1000repos.csv"
ck_base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "ck_m")
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

# ===== FUNÇÕES DE VISUALIZAÇÃO =====
def save_heatmap(df, charts_dir, method="spearman"):
    """Salva heatmap de correlação"""
    corr = df.corr(method=method)
    plt.figure(figsize=(9, 9))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title(f"Heatmap de Correlações ({method})")
    fname = f"Heatmap_{method}.png"
    plt.savefig(os.path.join(charts_dir, fname))
    plt.close()


def save_box(df, target, metric, charts_dir, rq_name):
    """Salva histograma e boxplot de uma métrica em relação ao target."""
    # Boxplot por quartis da variável independente
    try:
        df["group"] = pd.qcut(df[target], q=4, labels=["Q1","Q2","Q3","Q4"], duplicates="drop")
        sns.boxplot(x="group", y=metric, data=df)
        plt.xlabel(f"Quartis de {target}")
        plt.ylabel(metric)
        plt.title(f"Boxplot de {metric} por {target} ({rq_name})")
        fname = f"Box_{rq_name}_{metric}.png"
        plt.savefig(os.path.join(charts_dir, "boxplot", fname))
        plt.close()
    except ValueError as e:
        print_and_write(content=f"[!] Não foi possível criar boxplot para {metric} vs {target} ({rq_name}): {e}\n")

    df.drop(columns=["group"], inplace=True, errors="ignore")

def save_histogram(df, metric, charts_dir):
    # Histograma

    plt.hist(df[metric], bins=40, color="skyblue", edgecolor="black")
    plt.xlabel(metric)
    plt.ylabel("Frequência")
    plt.title(f"Histograma de {metric}")
    fname = f"Hist_{metric}.png"
    plt.savefig(os.path.join(charts_dir, "histogram", fname))
    plt.close()


def save_scatter(df, target, metric, charts_dir, rq_name, xlabel=None, ylabel=None):
    """Salva scatter plot entre target e metric."""

    plt.scatter(df[target], df[metric], alpha=0.6)
    plt.xlabel(xlabel if xlabel else target)
    plt.ylabel(ylabel if ylabel else metric)
    title = f"{rq_name}: {target} vs {metric}"
    plt.title(title)
    fname = f"Scatter_{rq_name}_{target}_vs_{metric}.png".replace(" ", "_")
    plt.savefig(os.path.join(charts_dir, "scatter", fname))
    plt.close()

# ===== FUNÇÕES PARA RQS =====
def analizar_rq01(df_final, charts_dir):
    """RQ01 - Popularidade x Qualidade"""
    print_and_write(content="\n=== RQ01 ===\n")

    # Correlações
    print_and_write(content=f"\nPearson:\n{df_final.corr(method='pearson')['stargazerCount']}\n")
    print_and_write(content=f"\nSpearman:\n{df_final.corr(method='spearman')['stargazerCount']}\n")

    # Gráficos
    metrics = ["loc", "cbo_mean", "dit_mean", "lcom_mean"]
    for metric in metrics:
        save_scatter(df_final, "stargazerCount", metric, charts_dir, "RQ01",
                     xlabel="Stars (popularidade)", ylabel=metric.upper())
        save_box(df_final.copy(), "stargazerCount", metric, charts_dir, "RQ01")

def analizar_rq02(df_final, charts_dir):
    """RQ02 - Maturidade x Qualidade"""
    print_and_write(content="\n=== RQ02 ===\n")

    # Correlações com maturidade (idade)
    pearson_corr = df_final.corr(method="pearson")["age_years"]
    spearman_corr = df_final.corr(method="spearman")["age_years"]
    print_and_write(content=f"\nPearson:\n{pearson_corr}\n")
    print_and_write(content=f"\nSpearman:\n{spearman_corr}\n")

    # Gráficos
    metrics = ["loc", "cbo_mean", "dit_mean", "lcom_mean"]
    for metric in metrics:
        save_scatter(df_final, "age_years", metric, charts_dir, "RQ02",
                     xlabel="Idade (anos)", ylabel=metric.upper())
        save_box(df_final.copy(), "age_years", metric, charts_dir, "RQ02")

def analizar_rq03(df_final, charts_dir):
    """RQ03 - Atividade x Qualidade"""
    print_and_write(content="\n=== RQ03 ===\n")

    # Correlações com atividade (número de releases)
    pearson_corr = df_final.corr(method="pearson")["releases"]
    spearman_corr = df_final.corr(method="spearman")["releases"]
    print_and_write(content=f"\nPearson:\n{pearson_corr}\n")
    print_and_write(content=f"\nSpearman:\n{spearman_corr}\n")

    # Gráficos
    metrics = ["loc", "cbo_mean", "dit_mean", "lcom_mean"]
    for metric in metrics:
        save_scatter(df_final, "releases", metric, charts_dir, "RQ03",
                     xlabel="Número de releases (atividade)", ylabel=metric.upper())
        save_box(df_final.copy(), "releases", metric, charts_dir, "RQ03")


def analizar_rq04(df_final, charts_dir):
    """RQ04 - Tamanho x Qualidade"""
    print_and_write(content="\n=== RQ04 ===\n")

    # Correlações com tamanho (LOC)
    pearson_corr = df_final.corr(method="pearson")["loc"]
    spearman_corr = df_final.corr(method="spearman")["loc"]
    print_and_write(content=f"\nPearson:\n{pearson_corr}\n")
    print_and_write(content=f"\nSpearman:\n{spearman_corr}\n")

    # Gráficos
    metrics = ["cbo_mean", "dit_mean", "lcom_mean"]
    for metric in metrics:
        save_scatter(df_final, "loc", metric, charts_dir, "RQ04",
                     xlabel="LOC (tamanho)", ylabel=metric.upper())
        save_box(df_final.copy(), "loc", metric, charts_dir, "RQ04")


def calc_stats(df_final, charts_dir):
    save_heatmap(df_final, charts_dir, method="spearman")
    save_heatmap(df_final, charts_dir, method="pearson")

    metrics = ["cbo_mean", "dit_mean", "lcom_mean", "loc"]
    for metric in metrics:
        save_histogram(df_final.copy(), metric, charts_dir)

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
    
    before = len(df_final)
    OUTLIER_METRICS = ["lcom_mean", "loc"]
    p96 = {}
    for metric in OUTLIER_METRICS:
        if metric in df_final.columns:
            p96[metric] = df_final[metric].quantile(0.96)
                
    for metric, threshold in p96.items():
        df_final = df_final[df_final[metric] <= threshold]
            
    after = len(df_final)
    print_and_write(content=f"[i] Removidos {before - after} outliers de {OUTLIER_METRICS} (>{p96})\n")
    print_and_write(content=f"[i] Dataset final com {len(df_final)} repositórios\n")

    data_length = len(df_final)
    charts_dir = os.path.join("../charts", f"charts_{data_length}_repos")
    os.makedirs(charts_dir, exist_ok=True)
    os.makedirs(os.path.join(charts_dir, "histogram"), exist_ok=True)
    os.makedirs(os.path.join(charts_dir, "boxplot"), exist_ok=True)
    os.makedirs(os.path.join(charts_dir, "scatter"), exist_ok=True)

    numeric_df = df_final.select_dtypes(include='number')

    calc_stats(numeric_df, charts_dir)
    analizar_rq01(numeric_df, charts_dir)
    analizar_rq02(numeric_df, charts_dir)
    analizar_rq03(numeric_df, charts_dir)
    analizar_rq04(numeric_df, charts_dir)

def print_and_write(file_path=metrics_path, content=""):
    with open(file_path, "a") as f:
        f.write(content)
    print(content)