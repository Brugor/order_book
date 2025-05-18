from pandas import read_csv as pd_read_csv
from dotenv import load_dotenv
from get_data.api import TelegramAlerta

# Carrega variáveis de ambiente do arquivo seguro
load_dotenv("alerta_vol_bot.env")


def carregar_limite(symbol, accumulated, coluna):
    path = f"get_data/data/{symbol}_{accumulated}_stat.csv"
    try:
        df = pd_read_csv(path)
        if coluna not in df.columns:
            raise ValueError(f"Coluna '{coluna}' não encontrada em {path}")
        limite = float(df[coluna].iloc[0])

        ajuste = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "1d": 86400}.get(
            accumulated, 1
        )
        return limite / ajuste if ajuste > 1 else limite
    except Exception:
        print(f"Erro ao carregar estatísticas: {Exception}")
        return None


def analisar_order_book(order_book, symbol, limit, coluna, accumulated):
    print(
        f"\nAnalisando order book para {symbol} com base em {coluna} ({accumulated})..."
    )
    limite = carregar_limite(symbol, accumulated, coluna)
    if limite is None:
        return

    last_vol_float = float(order_book.get("lastQty", 0))
    last_price_float = float(order_book.get("lastPrice", 0))

    print(f"\nVol alerta: {limite:.5f}")
    print(f"Vol atual: {last_vol_float:.5f}")
    print(f"Diferença: {(last_vol_float - limite):.5f}")

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
            f"Negociado - Alerta: {(last_vol_float - limite):.5f}\n",
            f"\n*Excessos detectados:*\n",
        ]
        for tipo, preco, vol in alertas:
            mensagem.append(f"[{tipo}] Preço: {float(preco):.2f} Vol: {vol:.5f}")
        telegram = TelegramAlerta()
        telegram.enviar("\n".join(mensagem))
