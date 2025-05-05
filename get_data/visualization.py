import matplotlib.pyplot as plt
import numpy as np


def plot_order_book(order_book: dict, symbol: str):
    """Gera um gráfico visual do order book"""
    try:
        # Converte para arrays numpy para manipulação
        bids = np.array(order_book["bids"], dtype=float)
        asks = np.array(order_book["asks"], dtype=float)

        # Ordena asks em ordem crescente para plotagem
        asks = asks[asks[:, 0].argsort()]

        # Configuração do gráfico
        plt.figure(figsize=(12, 6))
        plt.title(f"Order Book - {symbol}")

        # Plot bids (compra - verde)
        plt.bar(
            bids[:, 0], bids[:, 1], width=0.2, color="green", label="Bids (Compras)"
        )

        # Plot asks (venda - vermelho)
        plt.bar(asks[:, 0], asks[:, 1], width=0.2, color="red", label="Asks (Vendas)")

        # Linha do spread
        spread = asks[0, 0] - bids[0, 0]
        plt.axvline(
            x=bids[0, 0],
            color="blue",
            linestyle="--",
            label=f"Melhor Bid {bids[0, 0]:.2f}",
        )

        plt.axvline(
            x=asks[0, 0],
            color="orange",
            linestyle="--",
            label=f"Melhor Ask: {asks[0, 0]:.2f}",
        )

        # Anotação do spread
        mid_price = (bids[0, 0] + asks[0, 0]) / 2
        max_quantity = max(bids[:, 1].max(), asks[:, 1].max())

        plt.annotate(
            f"Spread {spread:.4f}",
            xy=(mid_price, max_quantity * 0.9),
            xytext=(mid_price, max_quantity * 0.95),
            ha="center",
            arrowprops=dict(facecolor="black", shrink=0.05),
        )

        plt.xlabel("Preço")
        plt.ylabel("Quantidade")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        raise
