import argparse
from datetime import datetime
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

                all_data.extend(data)
                last_timestamp = data[-1][0]
                start_ms = last_timestamp + 1
                time.sleep(0.2)  # evitar limite de requisições

            except requests.RequestException as e:
                print(f"\nErro na requisição: {e}")
                return None

        if not all_data:
            print("\nNenhum dado retornado.")
            return None

        filename = f"{path_file}/{symbol}_{interval}.csv"
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Ativo", "Data", "Intervalo", "Volume"])
                for entry in all_data:
                    writer.writerow(
                        [
                            symbol,
                            datetime.fromtimestamp(entry[0] / 1000).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            interval,
                            float(entry[5]),
                        ]
                    )
            print(f"\nDados salvos em: {filename}")
            return filename
        except IOError as e:
            print(f"Erro ao salvar arquivo: {e}")
            return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Consulta volume de negociação na Binance"
    )
    parser.add_argument("symbol", help="Ex: BTCUSDT")
    parser.add_argument("start_date", help="Data inicial (YYYY-MM-DD)")
    parser.add_argument("end_date", help="Data final (YYYY-MM-DD)")
    parser.add_argument("interval", choices=["5m", "15m", "1h", "1d"], help="Intervalo")
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
