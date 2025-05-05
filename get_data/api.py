import requests

class BinancePublicAPI:
    base_url = "https://api.binance.com/api/v3"

    def get_order_book(self, symbol: str = "BTCUSDT", limit: int = 10) -> dict:
        endpoint = f"{self.base_url}/depth"
        params = {'symbol': symbol.upper(), 'limit': limit}

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar API: {e}")
            return None