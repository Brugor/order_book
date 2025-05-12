import argparse
from datetime import datetime, time
import time as time_module
import json
import os
import sys
import subprocess
import requests
from .api import BinancePublicAPI
from .visualization import plot_order_book


def parse_args():
    parser = argparse.ArgumentParser(
        description="Order Book Viewer com Atualização Automática",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--symbol",
        default="BTCUSDT",
        help="Padrão: BTCUSDT. Código do ativo para busca (ex: BTCUSDT, ETHUSDT)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=19,
        help="Padrão: int 10. Número de ordens no book (máx 5000)",
    )

    parser.add_argument(
        "--plot", action="store_true", help="Exibe gráfico do order book"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Padrão: int 5. Intervalo mínimo de atualização em segundos",
    )
    parser.add_argument(
        "--start-time",
        type=str,
        default=None,
        help="Padrão: None. Hora de início (formato HH:MM)",
    )

    parser.add_argument(
        "--end-time",
        type=str,
        default=None,
        help="Padrão: None. Hora de término (formato HH:MM)",
    )

    parser.add_argument(
        "--coluna",
        type=str,
        default="D10",
        help="Padrão: D10. Indica a coluna que deve ser referência nas estatísticas",
    )

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
        time_module.sleep(1)
    return True


def should_continue(end_time_str):
    if not end_time_str:
        return True

    end_time = datetime.strptime(end_time_str, "%H:%M").time()
    return datetime.now().time() < end_time


def get_ticker_24h(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol.upper()}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao obter dados de ticker 24h: {e}")
        return {}


def salvar_order_book_temp(symbol, data):
    os.makedirs("get_data/temp", exist_ok=True)
    path = f"get_data/temp/{symbol}_order_book.json"
    with open(path, "w") as f:
        json.dump(data, f)


def chamar_cross_data(symbol, limit, coluna):
    try:
        subprocess.run(
            [
                sys.executable,
                "get_data/cross_data.py",
                symbol,
                "--limit",
                str(limit),
                "--coluna",
                coluna,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar cross_data.py: {e}")


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
            start_time = time_module.time()

            order_book = api.get_order_book(args.symbol, args.limit)
            ticker = get_ticker_24h(args.symbol)

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
                salvar_order_book_temp(args.symbol, order_book)

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

                if args.plot:
                    plot_order_book(order_book, args.symbol)

                chamar_cross_data(args.symbol, args.limit, args.coluna)

            elapsed = time_module.time() - start_time
            sleep_time = max(5, args.interval - elapsed)

            print(f"\nPróxima atualização em {sleep_time:.1f} segundos...")
            time_module.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nColeta interrompida pelo usuário")
