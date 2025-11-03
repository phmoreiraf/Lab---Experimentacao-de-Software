# main.py
# Menu simples para executar o pipeline completo reaproveitando a estrutura.

from analysis_rqs import build_bi_outputs, generate_report_md
from dataset import build_daily_tables, fetch_latest_measurements


def _menu():
    print("\n== LAB-04: Dashboard com dados públicos ==")
    print("1. Coletar dados (OpenAQ, últimos 180 dias)")
    print("2. Processar (diário por cidade/parâmetro)")
    print("3. Exportar para BI (fato/dimensões + agregados)")
    print("4. Gerar Relatório (docs/report_alt.md)")
    print("5. Executar tudo (1→4)")
    print("6. Sair")
    return input("Escolha uma opção: ").strip()

def main():
    try:
        while True:
            op = _menu()
            if op == "1":
                days = input("Quantos dias (padrão 180)? ").strip() or "180"
                fetch_latest_measurements(days=int(days))
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
                fetch_latest_measurements(days=180)
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
