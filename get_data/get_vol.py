import argparse
from datetime import datetime, timedelta
from api import BinancePublicAPI


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

    fetcher = BinancePublicAPI()
    print(">>> Chamando fetch_volume()")
    fetcher.fetch_volume(args.symbol, start, end, args.interval)


if __name__ == "__main__":
    main()
