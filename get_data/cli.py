from datetime import datetime
from time import sleep as time_sleep, time as time_time
from get_data.api import BinancePublicAPI
from get_data.args_config import ArgumentBuilder
from get_data.cross_data import analisar_order_book


def parse_args():
    parser = ArgumentBuilder.with_times_and_limit()
    return parser.parse_args()


def wait_until_start_time(start_time_str):
    if not start_time_str:
        return True

    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    now = datetime.now().time()

    if now >= start_time:
        return True

    print(f"Aguardando hora de início ({start_time_str})...")
    while datetime.now().time() < start_time:
        time_sleep(1)
    return True


def should_continue(end_time_str):
    if not end_time_str:
        return True

    end_time = datetime.strptime(end_time_str, "%H:%M").time()
    return datetime.now().time() < end_time


def execute_cli():
    args = parse_args()
    api = BinancePublicAPI()

    if args.interval < 5:
        print("Intervalo mínimo de 5 segundos forçado.")
        args.interval = 5

    if args.start_time:
        wait_until_start_time(args.start_time)

    try:
        while should_continue(args.end_time):
            start_time = time_time()

            order_book = api.get_order_book(args.symbol, args.limit)
            ticker = api.get_ticker_24h(args.symbol)

            if order_book:
                # Mesclar dados do ticker ao order_book
                order_book.update(
                    {
                        "lastPrice": ticker.get("lastPrice"),
                        "lastQty": ticker.get("lastQty"),
                        "bidPrice": ticker.get("bidPrice"),
                        "askPrice": ticker.get("askPrice"),
                    }
                )
                print("\033c", end="")

                print(f"Hora da coleta: {datetime.now().strftime('%H:%M:%S')}")
                print("Top 5 Bids (COMPRA):\n")
                for bid in order_book["bids"][:5]:
                    print(f"Preço: {float(bid[0]):.2f} Quantidade: {float(bid[1]):.5f}")

                print("\nTop 5 Asks (VENDAS):\n")
                for ask in order_book["asks"][:5]:
                    print(f"Preço: {float(ask[0]):.2f} Quantidade: {float(ask[1]):.5f}")

                if order_book["bids"] and order_book["asks"]:
                    best_bid = float(order_book["bids"][0][0])
                    best_ask = float(order_book["asks"][0][0])
                    spread = best_ask - best_bid
                    print(f"\nSpread: {spread:.4f} ({spread / best_bid * 100:.2f}%)\n")

                analisar_order_book(
                    order_book, args.symbol, args.limit, args.coluna, args.accumulated
                )

            elapsed = time_time() - start_time
            sleep_time = max(5, args.interval - elapsed)

            print(f"\nPróxima atualização em {sleep_time:.1f} segundos...")
            time_sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nColeta interrompida pelo usuário")
