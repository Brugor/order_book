import pandas as pd
import os
import argparse
import numpy as np


def gerar_estatisticas(symbol, interval):
    path = f"get_data/data/{symbol}_{interval}.csv"
    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}")
        return

    df = pd.read_csv(path)
    df["Volume"] = df["Volume"].astype(float)

    # Quartis
    q1 = df["Volume"].quantile(0.25)
    q2 = df["Volume"].quantile(0.50)
    q3 = df["Volume"].quantile(0.75)
    q4 = df["Volume"].max()

    # Decis (divisão em 10 partes)
    decimos = {}
    for i in range(1, 11):
        decimos[f"d{i}"] = df["Volume"].quantile(i / 10)

    # Criação do novo DataFrame
    estat = {"Q1": [q1], "Q2 (mediana)": [q2], "Q3": [q3], "Q4 (máximo)": [q4]}
    estat.update({k.upper(): [v] for k, v in decimos.items()})
    df_stat = pd.DataFrame(estat)

    output_path = f"get_data/data/{symbol}_{interval}_stat.csv"
    df_stat.to_csv(output_path, index=False)
    print(f"Estatísticas salvas em: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera estatísticas de volume")
    parser.add_argument("symbol", help="Símbolo, ex: BTCUSDT")
    parser.add_argument("interval", help="Intervalo, ex: 1d")
    args = parser.parse_args()

    gerar_estatisticas(args.symbol, args.interval)
