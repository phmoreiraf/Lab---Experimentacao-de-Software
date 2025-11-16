import pandas as pd
import os

# =============================
# 1. CARREGAR BASES
# =============================

DATA_DIR = os.path.join("data")

OUTPUT_DIR = os.path.join(DATA_DIR, "analysis")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

monthly_file = os.path.join(DATA_DIR, "raw", "openaq_brazil_monthly.csv")
yearly_file = os.path.join(DATA_DIR, "raw", "openaq_brazil_yearly.csv")
oms_limits_file = os.path.join(DATA_DIR, "oms", "oms_daily_limits.csv")
if not os.path.exists(monthly_file):
    raise FileNotFoundError(f"Arquivo não encontrado: {monthly_file}")
if not os.path.exists(yearly_file):
    raise FileNotFoundError(f"Arquivo não encontrado: {yearly_file}")
if not os.path.exists(oms_limits_file):
    raise FileNotFoundError(f"Arquivo não encontrado: {oms_limits_file}")

df = pd.read_csv(monthly_file)
oms = pd.read_csv(oms_limits_file)

if df.empty:
    print("Nenhum dado de sensores disponível para análise.")
    exit()

if oms.empty:
    print("Nenhum dado de limites da OMS disponível para análise.")
    exit()

# Remover espaços e normalizar nome dos poluentes
df["parameter_name"] = df["parameter_name"].str.lower().str.strip()
oms["pollutant"] = oms["pollutant"].str.lower().str.strip()

# Criar coluna de mês (YYYY-MM)
df["datetimeFrom_utc"] = pd.to_datetime(df["datetimeFrom_utc"], errors="coerce")
df["year_month"] = df["datetimeFrom_utc"].dt.to_period("M")

# =============================
# 2. CALCULAR MÉDIA MENSAL POR CIDADE E POLUENTE
# =============================

df_monthly_city = (
    df.groupby(["city", "parameter_name", "year_month"])["avg"]
      .mean()
      .reset_index()
      .rename(columns={"avg": "city_month_mean"})
)

# =============================
# 3. MESCLAR COM LIMITES DA OMS
# =============================

df_merged = df_monthly_city.merge(
    oms,
    left_on="parameter_name",
    right_on="pollutant",
    how="left"
)

# Remover poluentes sem limite definido
df_merged = df_merged.dropna(subset=["limit"])

# =============================
# 4. CALCULAR EXCEDÊNCIA MENSAL
# =============================

df_merged["exceeds"] = df_merged["city_month_mean"] > df_merged["limit"]

# =============================
# 5. CÁLCULO FINAL: PERCENTUAL DE EXCEDÊNCIA POR CIDADE E POLUENTE
# =============================

df_exceed_percent = (
    df_merged.groupby(["city", "parameter_name"])
             .agg(
                 months_total=("exceeds", "count"),
                 months_exceed=("exceeds", "sum")
             )
             .reset_index()
)

df_exceed_percent["percent_exceedance"] = (
    df_exceed_percent["months_exceed"] / df_exceed_percent["months_total"] * 100
)

# =============================
# 6. SALVAR RESULTADOS
# =============================

df_exceed_percent.to_csv(os.path.join(OUTPUT_DIR, "percentual_excedencia_por_cidade.csv"), index=False, encoding="utf-8-sig")
print("Arquivo salvo: percentual_excedencia_por_cidade.csv")

# ==========================================================
# 7. RANKING DAS CIDADES COM MAIORES MÉDIAS ANUAIS DE POLUENTES
# ==========================================================

# Criar coluna de ano
df["year"] = df["datetimeFrom_utc"].dt.year

# Média anual por cidade e por poluente
df_annual_city = (
    df.groupby(["city", "parameter_name", "year"])["avg"]
      .mean()
      .reset_index()
      .rename(columns={"avg": "city_year_mean"})
)

# Ranking geral por poluente, agregando média das médias anuais
# Para cada poluente, gerar um ranking separado
df_annual_city_clean = df_annual_city.query("parameter_name in ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co']")
pollutants = df_annual_city_clean["parameter_name"].unique()

rankings_dir = os.path.join(OUTPUT_DIR, "rankings_por_poluente")
os.makedirs(rankings_dir, exist_ok=True)

for pollutant in pollutants:
    df_pollutant = (
        df_annual_city_clean[df_annual_city_clean["parameter_name"] == pollutant]
        .groupby(["city"])["city_year_mean"]
        .mean()
        .reset_index()
        .sort_values(by="city_year_mean", ascending=False)
    )

    # Salvar o ranking individual
    filename = f"{rankings_dir}/ranking_{pollutant}.csv"
    df_pollutant.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"Arquivo salvo: {filename}")

df_city_pollutant_ranking = (
    df_annual_city_clean.groupby(["city", "parameter_name"])["city_year_mean"]
                  .mean()
                  .reset_index()
)

# Ordenar do mais poluído para o menos
df_city_pollutant_ranking = df_city_pollutant_ranking.sort_values(
    by="city_year_mean",
    ascending=False
)

df_city_pollutant_ranking.to_csv(os.path.join(OUTPUT_DIR, "ranking_cidades_por_poluente.csv"), index=False, encoding="utf-8-sig")
print("Arquivo salvo: ranking_cidades_por_poluente.csv")


# ==========================================================
# 8. GERAR CSV COM INFORMAÇÕES POR CIDADE
# ==========================================================
df_yearly = pd.read_csv(yearly_file)


# Total de sensores por cidade
sensores_por_cidade = (
    df_yearly.groupby("city")["sensor_id"]
             .nunique()
             .reset_index()
             .rename(columns={"sensor_id": "total_sensores"})
)

# Período de coleta por cidade
periodo_por_cidade = (
    df_yearly.groupby("city")
        .agg(
            data_inicio=("datetimeFrom_utc", "min"),
            data_fim=("datetimeTo_utc", "max"),
            percent_coverage_medio=("percentCoverage", "mean")
        )
        .reset_index()
)

# Converter percentCoverage → anos equivalentes de coleta
periodo_por_cidade["anos_equivalentes"] = periodo_por_cidade["percent_coverage_medio"] / 100

# Unir tudo
info_cidades = sensores_por_cidade.merge(periodo_por_cidade, on="city", how="left")

# Salvar CSV
info_cidades.to_csv(os.path.join(OUTPUT_DIR, "info_sensores_por_cidade.csv"), index=False, encoding="utf-8-sig")

print("Arquivo salvo: info_sensores_por_cidade.csv")
