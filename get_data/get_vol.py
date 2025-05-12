import argparse
from datetime import datetime, timedelta
import csv
import requests
import os
import time


class VolumeFetcher:
    BASE_URL = "https://api.binance.com/api/v3"

    def fetch_volume(self, symbol, start_date, end_date, interval):
        """Consulta dados de volume da Binance e salva em CSV"""
        path_file = "get_data/data"
        os.makedirs(path_file, exist_ok=True)

        filename = f"{path_file}/{symbol}_{interval}.csv"
        existing_data = []
        existing_dates = set()

        if os.path.exists(filename):
            print(f"\nArquivo existente encontrado: {filename}")
            with open(filename, "r") as f:
                reader = csv.reader(f)
                next(reader)  # pula o cabeçalho
                for row in reader:
                    existing_data.append(row)
                    try:
                        dt = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                        existing_dates.add(dt.date())
                    except Exception:
                        continue

        print(f"\nConsultando volume de {symbol}")
        print(
            f"Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}"
        )
        print(f"Intervalo: {interval}")

        start_ms = int(start_date.timestamp() * 1000)
        end_ms = int(end_date.timestamp() * 1000)
        limit = 1000
        all_data = []

        while start_ms < end_ms:
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "startTime": start_ms,
                "endTime": end_ms,
                "limit": limit,
            }

            try:
                response = requests.get(f"{self.BASE_URL}/klines", params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                for entry in data:
                    candle_time = datetime.fromtimestamp(entry[0] / 1000)
                    if candle_time.date() not in existing_dates:
                        all_data.append(
                            [
                                symbol,
                                candle_time.strftime("%Y-%m-%d %H:%M:%S"),
                                interval,
                                float(entry[5]),
                            ]
                        )

                last_timestamp = data[-1][0]
                start_ms = last_timestamp + 1
                time.sleep(0.3)

            except requests.RequestException as e:
                print(f"\nErro na requisição: {e}")
                return None

        if not all_data:
            print("\nNenhum novo dado a adicionar.")
        else:
            print(f"\n{len(all_data)} novos registros serão adicionados.")

        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Ativo", "Data", "Intervalo", "Volume"])
                combined = existing_data + all_data
                combined.sort(key=lambda x: x[1])
                for row in combined:
                    writer.writerow(row)
            print(f"\nDados salvos em: {filename}")
            return filename
        except IOError as e:
            print(f"Erro ao salvar arquivo: {e}")
            return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Consulta volume de negociação na Binance"
    )
    parser.add_argument("symbol", nargs="?", default="BTCUSDT", help="Ex: BTCUSDT")
    parser.add_argument(
        "start_date",
        nargs="?",
        default=(datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d"),
        help="Data inicial (YYYY-MM-DD)",
    )
    parser.add_argument(
        "end_date",
        nargs="?",
        default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        help="Data final (YYYY-MM-DD)",
    )
    parser.add_argument(
        "interval",
        nargs="?",
        choices=["1m", "5m", "15m", "1h", "1d"],
        default="1d",
        help="Intervalo",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        start = datetime.strptime(args.start_date, "%Y-%m-%d")
        end = datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError as e:
        print(f"Erro ao converter datas: {e}")
        return

    if start >= end:
        print("Data inicial deve ser anterior à data final.")
        return

    fetcher = VolumeFetcher()
    print(">>> Chamando fetch_volume()")
    fetcher.fetch_volume(args.symbol, start, end, args.interval)


if __name__ == "__main__":
    main()
