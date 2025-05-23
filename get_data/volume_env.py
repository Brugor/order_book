from numpy import array as np_array, float32 as np_float32
from pandas import read_csv as pd_read_csv
from json import dump as json_dump
from os import path as os_path, makedirs as os_makedirs
from datetime import datetime


class BinanceVolumeEnv:
    """
    Ambiente de aprendizado por reforço baseado em volume e preço da Binance.
    A ação do agente é decidir se deve comprar, vender ou ficar parado
    com base no volume recente de negociação e outros sinais.
    """

    def __init__(self, csv_path, symbol="BTCUSDT", initial_balance=10000.0, fee=0.001):
        self.df = pd_read_csv(csv_path)
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0.0  # quantidade comprada
        self.entry_price = 0.0
        self.fee = fee
        self.current_step = 0
        self.done = False
        self.trades = []
        self.log_path = f"logs/{symbol}_trades.json"
        os_makedirs(os_path.dirname(self.log_path), exist_ok=True)

    def reset(self):
        self.balance = self.initial_balance
        self.position = 0.0
        self.entry_price = 0.0
        self.current_step = 0
        self.done = False
        self.trades.clear()
        return self._get_state()

    def _get_state(self):
        row = self.df.iloc[self.current_step]
        return np_array(
            [
                float(row["Volume"]),
                float(row["Preço"]),
                float(self.position),
                float(self.balance),
            ],
            dtype=np_float32,
        )

    def step(self, action):
        if self.done:
            return self._get_state(), 0, self.done, {}

        row = self.df.iloc[self.current_step]
        preco = float(row["Preço"])
        data = row.get("Data") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        reward = 0

        if action == 1:  # BUY
            if self.position == 0:
                quantidade = self.balance / preco
                self.position = quantidade * (1 - self.fee)
                self.entry_price = preco
                self.balance = 0
                self.trades.append(
                    {
                        "step": self.current_step,
                        "timestamp": data,
                        "tipo": "BUY",
                        "preco": preco,
                        "volume": self.position,
                        "saldo": self.balance,
                    }
                )

        elif action == 2:  # SELL
            if self.position > 0:
                self.balance = self.position * preco * (1 - self.fee)
                reward = self.balance - self.initial_balance
                self.trades.append(
                    {
                        "step": self.current_step,
                        "timestamp": data,
                        "tipo": "SELL",
                        "preco": preco,
                        "volume": self.position,
                        "saldo": self.balance,
                        "lucro": reward,
                    }
                )
                self.position = 0
                self.entry_price = 0

        # HOLD = 0: sem ação

        self.current_step += 1
        if self.current_step >= len(self.df) - 1:
            self.done = True
            self._save_trades()

        return self._get_state(), reward, self.done, {}

    def _save_trades(self):
        with open(self.log_path, "w") as f:
            json_dump(self.trades, f, indent=2)

    def render(self):
        print(
            f"Passo: {self.current_step}, Saldo: {self.balance:.2f}, Posicao: {self.position:.5f}"
        )
        if self.trades:
            print("Trades recentes:")
            for trade in self.trades[-5:]:
                print(trade)
