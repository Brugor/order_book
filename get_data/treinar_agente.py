from os import path as os_path
from volume_env import BinanceVolumeEnv
from volume_agent import VolumeAgent
from args_config import ArgumentBuilder


def treinar_agente(csv_path, symbol, episodes=50):
    env = BinanceVolumeEnv(csv_path=csv_path, symbol=symbol)
    agent = VolumeAgent(state_size=4, action_size=3, symbol=symbol)

    for ep in range(episodes):
        print(f"\nIniciando Episódio {ep + 1}/{episodes} para {symbol}")
        state = env.reset()
        done = False
        total_reward = 0

        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, _ = env.step(action)
            agent.learn(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward

        env.render()
        print(f"Recompensa Total: {total_reward:.2f}")

    agent.save_q_table()
    print(f"\nAgente treinado e Q-table salva em logs/{symbol}_q_table.json")


if __name__ == "__main__":

    parser = ArgumentBuilder.with_episodes()
    args = parser.parse_args()

    csv_path = f"get_data/data/{args.symbol}_{args.accumulated}.csv"

    if not os_path.exists(csv_path):
        print(f"Arquivo CSV não encontrado: {csv_path}")
    else:
        treinar_agente(csv_path, args.symbol, args.episodes)
