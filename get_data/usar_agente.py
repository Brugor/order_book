from volume_agent import VolumeAgent
from api import BinancePublicAPI, TelegramAlerta
from numpy import array as np_array, float32 as np_float32
from time import sleep as time_sleep
from os import path as os_path, makedirs as os_makedirs
from csv import writer as csv_writer
from datetime import datetime


def usar_agente_ao_vivo(symbol="BTCUSDT", accumulated="5m", intervalo=5):
    api = BinancePublicAPI()
    agent = VolumeAgent(state_size=4, action_size=3, symbol=symbol)
    telegram = TelegramAlerta()
    saldo = 1000.0
    posicao = 0.0
    preco_medio = 0.0

    ajuste = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "1d": 86400}.get(
        accumulated, 1
    )

    os_makedirs("logs", exist_ok=True)
    log_file = f"logs/{symbol}_decisions_log.csv"
    if not os_path.exists(log_file):
        with open(log_file, "w", newline="") as f:
            writer = csv_writer(f)
            writer.writerow(
                [
                    "Timestamp",
                    "Symbol",
                    "Action",
                    "Price",
                    "Volume",
                    "BestBid",
                    "BestAsk",
                    "Spread",
                    "Position",
                    "Balance",
                    "Reward",
                ]
            )

    print("\n🚀 Executando agente com dados reais da Binance...\n")

    try:
        while True:
            order_book = api.get_order_book(symbol, limit=5)
            ticker = api.get_ticker_24h(symbol)

            if not order_book or not ticker:
                print("❌ Erro ao obter dados da Binance. Retentando...")
                time_sleep(intervalo)
                continue

            preco = float(ticker.get("lastPrice", 0))
            volume = float(ticker.get("lastQty", 0))  # / ajuste
            bid_price = float(ticker.get("bidPrice", 0))
            ask_price = float(ticker.get("askPrice", 0))
            spread = ask_price - bid_price

            state = np_array([volume, preco, posicao, saldo], dtype=np_float32)

            action = agent.choose_action(state)

            controle_envio = 0.0
            reward = 0.0
            if action == 1 and saldo >= preco * volume:
                # BUY
                custo = preco * volume
                saldo -= custo
                preco_medio = (
                    ((preco_medio * posicao) + custo) / (posicao + volume)
                    if posicao > 0
                    else preco
                )
                posicao += volume
            elif action == 2 and posicao >= volume:
                # SELL
                receita = preco * volume
                saldo += receita
                lucro = receita - (preco_medio * volume)
                reward = lucro
                posicao -= volume
                if posicao == 0:
                    preco_medio = 0.0

            next_state = np_array([volume, preco, posicao, saldo], dtype=np_float32)
            agent.learn(state, action, reward, next_state, False)

            with open(log_file, "a", newline="") as f:
                writer = csv_writer(f)
                writer.writerow(
                    [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        symbol,
                        ["HOLD", "BUY", "SELL"][action],
                        f"{preco:.2f}",
                        f"{volume:.5f}",
                        f"{bid_price:.2f}",
                        f"{ask_price:.2f}",
                        f"{spread:.2f}",
                        f"{posicao:.5f}",
                        f"{saldo:.2f}",
                        f"{reward:.2f}",
                    ]
                )

            if action in [1, 2] and controle_envio != saldo:
                controle_envio = saldo
                mensagem = (
                    f"🚨 *AGENTE BINANCE*\n"
                    f"Símbolo: `{symbol}`\n"
                    f"Ação: {['HOLD', 'BUY', 'SELL'][action]}\n"
                    f"Preço: {preco:.2f} | Volume: {volume:.5f}\n"
                    f"Valor da Carteira: {posicao*preco:.2f}\n"
                    f"Posição: {posicao:.5f} | Saldo: {saldo:.2f}\n"
                    f"Saldo + Carteira: {posicao*preco+saldo:.2f}\n"
                    f"Lucro: {reward:.2f}"
                )
                telegram.enviar(mensagem)

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] Ação: {['HOLD','BUY','SELL'][action]} | "
                f"Preço: {preco:.2f} | Pos: {posicao:.5f} | Saldo: {saldo:.2f} | Cart: {posicao*preco:.2f} | Saldo + Cart: {posicao*preco+saldo:.2f} | Reward: {reward:.2f}"
            )

            time_sleep(intervalo)

    except KeyboardInterrupt:
        print("\n🛑 Execução interrompida pelo usuário. Salvando Q-table...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/{symbol}_q_table_{timestamp}.json"
        agent.save_q_table(filename=filename)
        print(f"✅ Q-table salva como: {filename}")


if __name__ == "__main__":
    usar_agente_ao_vivo()
