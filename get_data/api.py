from os import getenv, makedirs, path as os_path
from requests import get as requests_get, post as requests_post, RequestException
from datetime import datetime
from time import sleep as time_sleep
from csv import reader as csv_reader, writer as csv_writer


class BinancePublicAPI:
    base_url = "https://api.binance.com/api/v3"

    def get_order_book(self, symbol: str = "BTCUSDT", limit: int = 10) -> dict:
        """
        Obtém o livro de ordens (order book) para o ativo informado.

        Parâmetros:
            symbol (str): Par de ativos (ex: "BTCUSDT").
            limit (int): Quantidade de ordens a retornar. Aceitos: 5, 10, 20, 50, 100, 500, 1000, 5000.

        Retorna:
            dict: Dados do livro de ordens com as chaves:
                - lastUpdateId: ID da última atualização
                - bids: lista de [preço, quantidade] de compra
                - asks: lista de [preço, quantidade] de venda

        Exemplo de retorno:
        {
            "lastUpdateId": 123456789,
            "bids": [["10350.00", "0.5"], ["10349.00", "1.2"]],
            "asks": [["10351.00", "0.3"], ["10352.00", "2.0"]]
        }
        """
        valid_limits = {5, 10, 20, 50, 100, 1000, 5000}
        if limit not in valid_limits:
            raise ValueError(f"Limite inválido: {limit}. Aceitos: {valid_limits}.")

        endpoint = f"{self.base_url}/depth"
        params = {"symbol": symbol, "limit": limit}

        try:
            response = requests_get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException:
            print(f"Erro ao acessar API: {RequestException}")
            return None

    def get_ticker_24h(self, symbol: str) -> dict:
        """
        Retorna estatísticas das últimas 24h de negociação do ativo informado.

        Parâmetros:
            symbol (str): Par de ativos (ex: "BTCUSDT").

        Retorna:
            dict: Estatísticas de variação de preço, volume e preços atuais.

        Exemplo de retorno:
        {
            "symbol": "BTCUSDT",
            "priceChange": "250.00",
            "lastPrice": "103500.00",
            "lastQty": "0.012",
            "bidPrice": "103495.00",
            "askPrice": "103505.00",
            "volume": "1523.45",
            "quoteVolume": "158000000.00"
        }
        """
        endpoint = f"{self.base_url}/ticker/24hr"
        params = {"symbol": symbol}

        try:
            response = requests_get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except RequestException:
            print(f"Erro ao obter dados de ticker 24h: {RequestException}")
            return None

    def fetch_volume(self, symbol, start_date, end_date, interval):
        """
        Consulta dados históricos de volume de negociação para um par de ativos na Binance,
        compara com os dados já existentes no arquivo CSV local (se houver), adiciona somente
        os registros que ainda não existem, e salva o resultado consolidado.

        Parâmetros:
            symbol (str): Símbolo do ativo (ex: "BTCUSDT").
            start_date (datetime): Data inicial do período a ser consultado.
            end_date (datetime): Data final do período a ser consultado.
            interval (str): Intervalo do candle (ex: "1m", "5m", "1h", "1d").

        Retorna:
            str | None: Caminho do arquivo CSV salvo, ou None em caso de falha.

        Observações:
            - Os dados são gravados em 'get_data/data/{symbol}_{interval}.csv'.
            - Entradas duplicadas (por data) são ignoradas com base no conteúdo já presente.
            - Em caso de erro de conexão (RequestException), retorna None.
        """
        path_file = "get_data/data"
        makedirs(path_file, exist_ok=True)

        filename = f"{path_file}/{symbol}_{interval}.csv"
        existing_data = []
        existing_dates = set()

        if os_path.exists(filename):
            print(f"\nArquivo existente encontrado: {filename}")
            with open(filename, "r") as f:
                reader = csv_reader(f)
                next(reader)  # pula o cabeçalho
                for row in reader:
                    existing_data.append(row)
                    try:
                        dt = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                        existing_dates.add(dt.date())
                    except Exception:
                        continue

        print(f"\nConsultando volume de {symbol}")
        print(f"Período: {start_date} a {end_date}")
        print(f"Intervalo: {interval}")

        start_ms = int(start_date.timestamp() * 1000)
        end_ms = int(end_date.timestamp() * 1000)
        limit = 1000
        all_data = []

        while start_ms < end_ms:
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_ms,
                "endTime": end_ms,
                "limit": limit,
            }

            try:
                response = requests_get(f"{self.base_url}/klines", params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                for entry in data:
                    candle_time = datetime.fromtimestamp(entry[0] / 1000)
                    if candle_time.date() not in existing_dates:
                        all_data.append(
                            [
                                symbol,
                                candle_time.strftime("%Y-%m-%d %H:%M:%S"),
                                interval,
                                float(entry[5]),
                            ]
                        )

                last_timestamp = data[-1][0]
                start_ms = last_timestamp + 1
                time_sleep(0.3)

            except RequestException:
                print(f"\nErro na requisição: {RequestException}")
                return None

        if not all_data:
            print("\nNenhum novo dado a adicionar.")
        else:
            print(f"\n{len(all_data)} novos registros serão adicionados.")

        try:
            with open(filename, "w", newline="") as f:
                writer = csv_writer(f)
                writer.writerow(["Ativo", "Data", "Intervalo", "Volume"])
                combined = existing_data + all_data
                combined.sort(key=lambda x: x[1])
                for row in combined:
                    writer.writerow(row)
            print(f"\nDados salvos em: {filename}")
            return filename
        except IOError:
            print(f"Erro ao salvar arquivo: {IOError}")
            return None


class TelegramAlerta:
    """
    Classe responsável por enviar mensagens de alerta via Telegram
    usando as variáveis de ambiente TELEGRAM_TOKEN e TELEGRAM_CHAT_ID.
    """

    def __init__(self):
        self.token = getenv("TELEGRAM_TOKEN")
        self.chat_id = getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def enviar(self, mensagem: str) -> None:

        if not self.token or not self.chat_id:
            print("Token ou chat_id do Telegram não configurados.")
            return

        data = {
            "chat_id": self.chat_id,
            "text": mensagem,
            "parse_mode": "Markdown",
        }

        try:
            response = requests_post(self.api_url, data=data, timeout=5)
            response.raise_for_status()
            print("✅ Alerta enviado via Telegram.")
        except RequestException:
            print(f"Erro ao enviar alerta via Telegram: {RequestException}")
