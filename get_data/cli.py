import argparse
from .api import BinancePublicAPI
from .visualization import plot_order_book


def parse_args():
    parser = argparse.ArgumentParser(
        description="Binance Order Book Viewer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--symbol", default="BTCUSDT", help="Par de trading (ex: BTCUSDT), ETHUSDT)"
    )

    parser.add_argument(
        "--limit", type=int, default=10, help="Número de ordens no book (máx 5000)"
    )

    parser.add_argument(
        "--plot", action="store_true", help="Exibi gráfico do order book"
    )

    return parser.parse_args()


def execute_cli():
    args = parse_args()
    api = BinancePublicAPI()

    print(f"\nObtendo Order Book para {args.symbol}...")
    order_book = api.get_order_book(args.symbol, args.limit)

    if order_book:
        print(f"\nUltima atualização ID: {order_book.get('lastUpdateID', 'N/A')}")

        # Exibe bids e ask
        print("\nTop 5 Bids (COMPRAS):")
        for bid in order_book["bids"][:5]:
            print(f"Preço: {bid[0]:<12} Quantidade: {bid[1]}")

        print("\nTop 5 Asks (VENDAS):")
        for ask in order_book["asks"][:5]:
            print(f"Preço: {ask[0]:<12} Quantidade: {ask[1]}")

        # Calcula e exibe o spread
        if order_book["bids"] and order_book["asks"]:
            best_bid = float(order_book["bids"][0][0])
            best_ask = float(order_book["asks"][0][0])
            spread = best_ask - best_bid
            print(f"\nSpread: {spread:.4f} ({spread/best_bid*100:.2f}%)")

        # Plota gráfico se solicitado
        if args.plot:
            plot_order_book(order_book, args.symbol)


if __name__ == "__main__":
    execute_cli()
