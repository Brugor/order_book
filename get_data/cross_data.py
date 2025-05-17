import argparse
import pandas as pd
import os
import json
from dotenv import load_dotenv
from api import TelegramAlerta

# Carrega variáveis de ambiente do arquivo seguro
load_dotenv("alerta_vol_bot.env")


def ler_order_book_temp(symbol):
    path = f"get_data/temp/{symbol}_order_book.json"
    if not os.path.exists(path):
        print(f"Arquivo JSON do order book não encontrado: {path}")
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
        return None


def carregar_limite(symbol, interval, coluna):
    path = f"get_data/data/{symbol}_{interval}_stat.csv"
    try:
        df = pd.read_csv(path)
        if coluna not in df.columns:
            raise ValueError(f"Coluna '{coluna}' não encontrada em {path}")
        limite = float(df[coluna].iloc[0])

        ajuste = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "1d": 86400}.get(
            interval, 1
        )
        return limite / ajuste if ajuste > 1 else limite
    except Exception as e:
        print(f"Erro ao carregar estatísticas: {e}")
        return None


def comparar_volumes(symbol, limit, coluna="D10", interval="1m"):
    coluna = coluna.upper()
    print(f"Carregando limite da coluna {coluna}...")
    limite = carregar_limite(symbol, interval, coluna)
    if limite is None:
        return

    order_book = ler_order_book_temp(symbol)
    last_vol_float = float(order_book.get("lastQty", "-"))
    last_price_float = float(order_book.get("lastPrice", "-"))

    print(f"\nLendo order book temporário para {symbol}")
    print(f"\nVol alerta: {limite:.5f}")
    print(f"Vol atual: {last_vol_float:.5f}")
    print(f"Diferença: {(last_vol_float-limite):.5f}")

    if not order_book:
        print("Nenhum dado do order book disponível.")
        return

    alertas = []
    for side, nome in [("bids", "COMPRA"), ("asks", "VENDA")]:
        for preco, quantidade in order_book.get(side, [])[:limit]:
            volume = float(quantidade)
            if last_vol_float > limite:
                if volume > limite:
                    alertas.append((nome, preco, volume))

    if alertas:
        mensagem = [
            f"🚨 *ALERTA DE VOLUME*",
            f"\nSímbolo: `{symbol}`",
            f"\nÚltimo Preço: {last_price_float:.2f}",
            f"Última Quantidade: {last_vol_float:.5f}",
            f"Alerta a partir de: {limite:.5f}",
            f"Negociado - Alerta: {(last_vol_float-limite):.5f}\n",
            f"\n*Excessos detectados:*\n",
        ]
        for tipo, preco, vol in alertas:
            mensagem.append(f"[{tipo}] Preço: {float(preco):.2f} Vol: {vol:.5f}")
        telegram = TelegramAlerta()
        telegram.enviar("\n".join(mensagem))


def main():
    parser = argparse.ArgumentParser(
        description="Verifica volumes do order book com base nas estatísticas"
    )
    parser.add_argument("symbol", help="Símbolo do ativo (ex: BTCUSDT)")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limite de ordens no book para verificação de alertas",
    )
    parser.add_argument(
        "--coluna", default="D10", help="Coluna estatística a ser usada (padrão: D10)"
    )
    parser.add_argument(
        "--interval",
        default="1m",
        help="Intervalo do arquivo de estatística (1m, 5m, 15m, 1h, 1d)",
    )
    args = parser.parse_args()

    comparar_volumes(args.symbol, args.limit, args.coluna, args.interval)


if __name__ == "__main__":
    main()
