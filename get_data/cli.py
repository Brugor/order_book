import argparse
from datetime import datetime, time
import time as time_module
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

    # Argumento de Controle de Tempo
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Padrão: int 0. Intervalo de atualização em segundos",
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

    return parser.parse_args()


def wait_until_start_time(start_time_str):
    """Aguardar até a hora de início especificada"""
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
    """Verificar se deve continuar executando"""
    if not end_time_str:
        return True

    end_time = datetime.strptime(end_time_str, "%H:%M").time()
    return datetime.now().time() < end_time


def execute_cli():
    args = parse_args()
    api = BinancePublicAPI()

    # Aguardar hora de início solicitada
    if args.start_time:
        wait_until_start_time(args.start_time)

    try:
        while should_continue(args.end_time):
            start_time = time_module.time()

            print(f"\nObtendo order book para {args.symbol}...")
            order_book = api.get_order_book(args.symbol, args.limit)

            if order_book:
                print(
                    f"\nÚltima atualização ID: {order_book.get('lastUpdatedID', 'N/A')}"
                )
                print(f"Hora da coleta: {datetime.now().strftime('%H:%M:%S')}")

                # Exibe bids e asks
                print("\nTop 5 Bids (COMPRA):")
                for bid in order_book["bids"][:5]:
                    print(f"Preço: {bid[0]:<12} Quantidade: {bid[1]}")

                print("\nTop 5 Asks (VENDAS):")
                for ask in order_book["asks"][:5]:
                    print(f"Preço: {ask[0]:<12} Quantidade: {ask[1]}")

                if order_book["bids"] and order_book["asks"]:
                    best_bid = float(order_book["bids"][0][0])
                    best_ask = float(order_book["asks"][0][0])
                    spread = best_ask - best_bid
                    print(f"\nSpread: {spread:.4f} ({spread/best_bid*100:.2f}%)")

            # Plota gráfico se solicitado
            if args.plot:
                plot_order_book(order_book, args.symbol)

            # Calcula tempo restante do intervalo
            elapsed = time_module.time() - start_time
            sleep_time = max(0, args.interval - elapsed)

            if should_continue(args.end_time):
                print(f"\nPróxima atualização em {sleep_time:.1f} segundos...")
                time_module.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nColeta interrompida pelo usuário")
