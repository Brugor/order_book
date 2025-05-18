from api import BinancePublicAPI
from args_config import ArgumentBuilder


def main():
    parser = ArgumentBuilder.with_dates()
    args = parser.parse_args()

    try:
        start = args.start_date
        end = args.end_date
    except ValueError:
        print(f"Erro ao converter datas: {ValueError}")
        return

    if start >= end:
        print("Data inicial deve ser anterior à data final.")
        return

    fetcher = BinancePublicAPI()
    print(">>> Chamando fetch_volume()")
    fetcher.fetch_volume(args.symbol, start, end, args.accumulated)


if __name__ == "__main__":
    main()
