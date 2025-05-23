from argparse import (
    ArgumentParser as args_parser,
    ArgumentDefaultsHelpFormatter as args_default_help_formatter,
)
from datetime import datetime, timedelta


class ArgumentBuilder:
    """Classe para a construção de parsers de linha de comando"""

    @staticmethod
    def base_parser():
        parser = args_parser(formatter_class=args_default_help_formatter)
        parser.add_argument(
            "--symbol",
            type=str.upper,
            default="BTCUSDT",
            help="Padrão: BTCUSDT. Código do ativo para busca (ex: BTCUSDT, ETHUSDT)",
        )
        parser.add_argument(
            "--accumulated",
            type=str.lower,
            default="5m",
            help="Padrão: 5m. interval (str): Intervalo da soma dos dados. 5m tem o volume de 5 min de negociação (ex: '1m', '5m', '1h', '1d').",
        )
        return parser

    @staticmethod
    def with_dates():
        parser = ArgumentBuilder.base_parser()
        today = datetime.now()
        default_end = today - timedelta(days=1)
        default_start = today - timedelta(days=31)

        parser.add_argument(
            "--start_date",
            type=lambda d: datetime.strptime(d, "%Y-%m-%d"),
            default=default_start,
            help="Data inicial (YYYY-MM-DD)",
        )
        parser.add_argument(
            "--end_date",
            type=lambda d: datetime.strptime(d, "%Y-%m-%d"),
            default=default_end,
            help="Data final (YYYY-MM-DD)",
        )

        return parser

    @staticmethod
    def with_times_and_limit():
        parser = ArgumentBuilder.base_parser()
        parser.add_argument("--start_time", type=str, help="Hora de início (HH:MM)")
        parser.add_argument("--end_time", type=str, help="Hora de fim (HH:MM)")
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Padrão: 10. Quantidade de ordens a retornar. Aceitos: 5, 10, 20, 50, 100, 500, 1000, 5000.",
        )

        parser.add_argument(
            "--interval",
            type=int,
            default=5,
            help="Padrão: int 5. Intervalo mínimo de atualização em segundos",
        )

        parser.add_argument(
            "--coluna",
            type=str.upper,
            default="D10",
            help="Coluna estatística (ex: D9, D10)",
        )

        return parser

    @staticmethod
    def with_episodes():
        parser = ArgumentBuilder.base_parser()
        parser.add_argument(
            "--episodes",
            type=int,
            default=50,
            help="Número de episódios de treinamento",
        )
        return parser
