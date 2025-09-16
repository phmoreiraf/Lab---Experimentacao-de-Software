#!/usr/bin/env python
import os, pandas as pd

OUT = "reports/report.md"

def read_csv(path):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

def md_table(df):
    if df.empty: return "_Sem dados._\n"
    return df.to_markdown(index=False) + "\n"

def main():
    os.makedirs("reports", exist_ok=True)
    rq1 = read_csv("data/rq1_correlations.csv")
    rq2 = read_csv("data/rq2_correlations.csv")
    rq3 = read_csv("data/rq3_correlations.csv")
    rq4 = read_csv("data/rq4_loc_correlations.csv")

    content = f"""\
# Relatório Final — LAB02 (Qualidade em Sistemas Java)

> Sumário das análises conforme o enunciado: RQ1–RQ4 com correlações (Pearson/Spearman), medidas centrais por repositório e gráficos complementares.

## 1. Introdução e Hipóteses
- H1: Repositórios mais populares (stars) tendem a menor acoplamento médio (CBO).
- H2: Repositórios mais maduros (idade) tendem a maior coesão (menor LCOM).
- H3: Projetos com mais releases exibem métricas de qualidade mais estáveis.
- H4: Repositórios maiores (LOC) tendem a maior CBO e DIT.

## 2. Metodologia
- **Amostra:** top-N repositórios Java (GraphQL GitHub).
- **Processo:** idade (anos), releases e (opcional) stars.
- **Qualidade (CK):** CBO, DIT, LCOM, LOC, etc. (agregadas por repositório).
- **Análises:** estatística descritiva e correlações **Pearson/Spearman**.

## 3. Resultados

### RQ1 — Popularidade × Qualidade
{md_table(rq1)}

### RQ2 — Maturidade × Qualidade
{md_table(rq2)}

### RQ3 — Atividade × Qualidade
{md_table(rq3)}

### RQ4 — Tamanho (LOC) × Qualidade
{md_table(rq4)}

> Figuras em `data/figures/` e CSVs por par (X,Y) em `data/exports/`.

## 4. Discussão e Ameaças à Validade
- Correlações fracas porém significativas podem refletir tendências em amostras grandes.
- Diferenças entre Pearson e Spearman sugerem relações não-lineares ou outliers.
- Snapshot temporal; qualidade é dinâmica.

## 5. Conclusões e Próximos Passos
- Consolidar achados e, se necessário, aplicar modelos multivariados.
- Estratificar por domínio e tamanho do projeto.
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Relatório gerado em {OUT}")

if __name__ == "__main__":
    main()
