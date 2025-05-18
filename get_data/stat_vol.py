from pandas import read_csv as pd_read_csv, DataFrame
from os import path as os_path
from args_config import ArgumentBuilder


def gerar_estatisticas(symbol, accumulated):
    path_file = f"get_data/data/{symbol}_{accumulated}.csv"
    if not os_path.exists(path_file):
        print(f"Arquivo não encontrado: {path_file}")
        return

    df = pd_read_csv(path_file)
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
    df_stat = DataFrame(estat)

    output_path = f"get_data/data/{symbol}_{accumulated}_stat.csv"
    df_stat.to_csv(output_path, index=False)
    print(f"Estatísticas salvas em: {output_path}")


if __name__ == "__main__":
    parser = ArgumentBuilder.base_parser()
    args = parser.parse_args()

    gerar_estatisticas(args.symbol, args.accumulated)
