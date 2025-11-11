# main.py — Menu simples do pipeline
from analysis_rqs import build_bi_outputs, generate_report_md
from dataset import build_daily_tables, fetch_latest_measurements


def _menu():
    print("\n== LAB-04: Dashboard com dados públicos ==")
    print("1. Coletar dados (OpenAQ)")
    print("2. Processar (diário por cidade/parâmetro)")
    print("3. Exportar para BI (fato/dimensões + agregados)")
    print("4. Gerar Relatório (docs/report_alt.md)")
    print("5. Executar tudo (1→4)")
    print("6. Sair")
    return input("Escolha uma opção: ").strip()

def _ask_source_and_days():
    days = input("Quantos dias (padrão 365)? ").strip() or "365"
    print("Conjunto de cidades: [1] Capitais  [2] >500k  [3] Custom (UF:Cidade;UF:Cidade;...)")
    choice = input("Escolha (1/2/3) [padrão 2]: ").strip() or "2"
    if choice == "1":
        return int(days), "CAPITAIS", None
    if choice == "3":
        custom = input("Informe (ex.: SP:São Paulo;RJ:Rio de Janeiro): ").strip()
        return int(days), "CUSTOM", custom
    return int(days), "500K", None

def main():
    try:
        while True:
            op = _menu()
            if op == "1":
                days, city_set, custom = _ask_source_and_days()
                fetch_latest_measurements(days=days, city_set=city_set, custom_cities=custom)
                print("[✓] Coleta concluída (data/raw)")
            elif op == "2":
                build_daily_tables()
                print("[✓] Processamento concluído (data/processed)")
            elif op == "3":
                build_bi_outputs()
                print("[✓] Artefatos BI gerados (data/bi)")
            elif op == "4":
                generate_report_md()
                print("[✓] Relatório em docs/report_alt.md")
            elif op == "5":
                days, city_set, custom = _ask_source_and_days()
                fetch_latest_measurements(days=days, city_set=city_set, custom_cities=custom)
                build_daily_tables()
                build_bi_outputs()
                generate_report_md()
                print("[✓] Pipeline completo finalizado")
            else:
                print("Saindo...")
                break
    except Exception as e:
        print(f"[X] Erro: {e}")

if __name__ == "__main__":
    main()
