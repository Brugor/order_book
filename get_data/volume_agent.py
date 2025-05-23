from numpy import round as np_round, argmax as np_argmax, float32 as np_float32
from random import random as random_random, randint as random_randint
from os import path as os_path, makedirs as os_makedirs
from json import dump as json_dump, load as json_load
from re import sub as re_sub
import numpy as np


class VolumeAgent:
    """
    Agente de Q-learning tabular para decisões baseadas em volume e preço.
    """

    def __init__(
        self,
        state_size,
        action_size,
        symbol="BTCUSDT",
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.995,
        alpha=0.1,
        gamma=0.95,
    ):
        self.state_size = state_size
        self.action_size = action_size  # [0: HOLD, 1: BUY, 2: SELL]
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.alpha = alpha  # taxa de aprendizado
        self.gamma = gamma  # fator de desconto
        self.q_table = {}  # {(state): [q0, q1, q2]}
        self.symbol = symbol
        self.q_table_file = f"logs/{symbol}_q_table.json"
        os_makedirs("logs", exist_ok=True)
        self._load_q_table()

    def _state_to_key(self, state):
        return tuple(np_round(state, 2))

    def choose_action(self, state):
        state_key = self._state_to_key(state)
        if random_random() < self.epsilon:
            return random_randint(0, self.action_size - 1)

        self.q_table.setdefault(state_key, [0.0] * self.action_size)
        return int(np_argmax(self.q_table[state_key]))

    def learn(self, state, action, reward, next_state, done):
        state_key = self._state_to_key(state)
        next_key = self._state_to_key(next_state)

        self.q_table.setdefault(state_key, [0.0] * self.action_size)
        self.q_table.setdefault(next_key, [0.0] * self.action_size)

        target = reward
        if not done:
            target += self.gamma * max(self.q_table[next_key])

        self.q_table[state_key][action] += self.alpha * (
            target - self.q_table[state_key][action]
        )

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_q_table(self, filename=None):
        filename = filename or f"logs/{self.symbol}_q_table.json"
        serializable_q_table = {str(tuple(k)): v for k, v in self.q_table.items()}
        with open(filename, "w") as f:
            json_dump(serializable_q_table, f)

    """def _load_q_table(self):
        try:
            filename = f"logs/{self.symbol}_q_table.json"
            if os_path.exists(filename):
                with open(filename, "r") as f:
                    raw = json_load(f)
                self.q_table = {
                    tuple(map(float, k.strip("() ").split(","))): v
                    for k, v in raw.items()
                }
                print(f"Q-table carregada: {filename}")
            else:
                self.q_table = {}
        except Exception as e:
            print(f"Erro ao carregar Q-table: {e}")
            self.q_table = {}"""

    def _load_q_table(self):
        try:
            filename = f"logs/{self.symbol}_q_table.json"
            if os_path.exists(filename):
                with open(filename, "r") as f:
                    raw = json_load(f)

                def parse_key(k):
                    # Remove 'np.float32(...)' se presente
                    limpa = re_sub(r"np\.float32\(([^)]+)\)", r"\1", k)
                    return tuple(map(float, limpa.strip("() ").split(",")))

                def parse_value(v):
                    # Lista de floats
                    if isinstance(v, list):
                        return [float(x) for x in v]
                    try:
                        return float(v)
                    except Exception:
                        return 0.0

                self.q_table = {parse_key(k): parse_value(v) for k, v in raw.items()}
                print(f"✅ Q-table carregada com sucesso: {filename}")
            else:
                print(f"⚠️ Arquivo não encontrado. Iniciando Q-table vazia: {filename}")
                self.q_table = {}
        except Exception as e:
            print(f"❌ Erro ao carregar Q-table: {e}")
            print(f"Tipo do erro: {type(e).__name__}")
            self.q_table = {}
