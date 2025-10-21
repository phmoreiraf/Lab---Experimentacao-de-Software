
## Resumo das medias das Métricas
| Métrica                   |    N |      Média |   Desvio Padrão |   Mínimo |        Q1 |   Mediana |       Q3 |   Máximo |
|:--------------------------|-----:|-----------:|----------------:|---------:|----------:|----------:|---------:|---------:|
| size_files                | 5953 |    3.5834  |         5.71881 |  1       |   1       |    2      |    3     |     63   |
| size_additions            | 5953 |   63.7154  |       144.342   |  0       |   2       |   11      |   52     |   1276   |
| size_deletions            | 5953 |   23.2493  |        56.4071  |  0       |   1       |    3      |   17     |    463   |
| analysis_hours            | 5953 |  261.884   |       759.635   |  1.19944 |   7.53194 |   26.8783 |  122.762 |   6278.1 |
| desc_len_chars            | 5953 | 1046.39    |      1498.65    |  0       | 123       |  507      | 1306     |  10217   |
| interactions_participants | 5953 |    2.67176 |         1.0577  |  1       |   2       |    2      |    3     |      7   |
| interactions_comments     | 5953 |    2.64472 |         3.00793 |  0       |   1       |    2      |    4     |     17   |
| reviews_count             | 5953 |    1.97195 |         1.55014 |  1       |   1       |    1      |    2     |      9   |

## Análise RQ A – Feedback final das revisões

### Correlação de Spearman com 'final_status_bin' (MERGED=1):
| metric                    |        rho |           p | significant   |
|:--------------------------|-----------:|------------:|:--------------|
| size_deletions            |  0.134384  | 2.14935e-25 | YES           |
| size_files                |  0.128821  | 1.88702e-23 | YES           |
| size_additions            |  0.0631279 | 1.09075e-06 | YES           |
| desc_len_chars            |  0.0181485 | 0.16149     | NO            |
| interactions_participants | -0.0908672 | 2.15626e-12 | YES           |
| interactions_comments     | -0.115363  | 4.30396e-19 | YES           |
| analysis_hours            | -0.174021  | 1.08006e-41 | YES           |

### Teste de Mann–Whitney (diferença entre MERGED e CLOSED):
| metric                    |           U |           p | significant   |
|:--------------------------|------------:|------------:|:--------------|
| size_files                | 2.94299e+06 | 2.8318e-23  | YES           |
| size_additions            | 2.72117e+06 | 1.11452e-06 | YES           |
| size_deletions            | 2.991e+06   | 3.48045e-25 | YES           |
| analysis_hours            | 1.81437e+06 | 4.28183e-41 | YES           |
| desc_len_chars            | 2.5499e+06  | 0.161475    | NO            |
| interactions_participants | 2.15599e+06 | 2.37765e-12 | YES           |
| interactions_comments     | 2.04585e+06 | 5.57695e-19 | YES           |

## Análise RQ B – Número de revisões realizadas

### Correlação de Spearman com 'reviews_count':
| metric                    |      rho |            p | significant   |
|:--------------------------|---------:|-------------:|:--------------|
| interactions_comments     | 0.4219   | 1.23128e-255 | YES           |
| interactions_participants | 0.367726 | 5.10564e-190 | YES           |
| size_additions            | 0.227643 | 7.81694e-71  | YES           |
| size_files                | 0.177705 | 1.98044e-43  | YES           |
| size_deletions            | 0.111063 | 8.40119e-18  | YES           |
| desc_len_chars            | 0.106725 | 1.50277e-16  | YES           |
| analysis_hours            | 0.09239  | 9.18493e-13  | YES           |

---
Análise concluída. Resultados salvos em 'data/metrics_report.md' e gráficos em 'charts/'.
