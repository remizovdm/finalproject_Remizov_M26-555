import argparse
import shlex

from valutatrade_hub.core import usecases
from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)


def create_parser():
    """Создание парсера командной строки"""
    parser = argparse.ArgumentParser(
        description="ValutaTrade Hub"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("update-rates")

    rates_parser = subparsers.add_parser("show-rates")
    rates_parser.add_argument("--currency")
    rates_parser.add_argument("--top", type=int)

    register_parser = subparsers.add_parser("register")
    register_parser.add_argument("--username", required=True)
    register_parser.add_argument("--password", required=True)

    login_parser = subparsers.add_parser("login")
    login_parser.add_argument("--username", required=True)
    login_parser.add_argument("--password", required=True)

    portfolio_parser = subparsers.add_parser("show-portfolio")
    portfolio_parser.add_argument("--base", default="USD")

    buy_parser = subparsers.add_parser("buy")
    buy_parser.add_argument("--currency", required=True)
    buy_parser.add_argument("--amount", type=float, required=True)

    sell_parser = subparsers.add_parser("sell")
    sell_parser.add_argument("--currency", required=True)
    sell_parser.add_argument("--amount", type=float, required=True)

    rate_parser = subparsers.add_parser("get-rate")
    rate_parser.add_argument("--from", dest="from_currency", required=True)
    rate_parser.add_argument("--to", dest="to_currency", required=True)

    return parser


def main():
    """Запуск интерфейса командной строки"""
    parser = create_parser()

    print("Добро пожаловать в ValutaTrade Hub! Введите необходимую команду или введите 'exit' для выхода.")
    print(
        "\nКоманды:\n\n"
        "register — регистрация пользователя\n"
        "  register --username testuser --password 1234\n\n"
        "login — вход в систему\n"
        "  login --username testuser --password 1234\n\n"
        "show-portfolio — просмотр портфеля\n"
        "  show-portfolio --base USD\n\n"
        "buy — покупка валюты\n"
        "  buy --currency BTC --amount 0.01\n\n"
        "sell — продажа валюты\n"
        "  sell --currency BTC --amount 0.01\n\n"
        "get-rate — получение курса валют\n"
        "  get-rate --from BTC --to USD\n\n"
        "show-rates — просмотр курсов из кеша\n"
        "  show-rates\n"
        "  show-rates --currency BTC\n"
        "  show-rates --top 2\n\n"
        "update-rates — обновление курсов\n"
        "  update-rates\n\n"
        "exit — выход из программы\n"
    )

    while True:
        command = input("> ").strip()

        if command.lower() == "exit":
            break

        if not command:
            continue

        try:
            args = parser.parse_args(shlex.split(command))
            if args.command == "register":
                usecases.register(args.username, args.password)
            elif args.command == "login":
                usecases.login(args.username, args.password)
            elif args.command == "show-portfolio":
                usecases.show_portfolio(args.base)
            elif args.command == "buy":
                usecases.buy(args.currency, args.amount)
            elif args.command == "sell":
                usecases.sell(args.currency, args.amount)
            elif args.command == "get-rate":
                rate, updated_at = usecases.get_rate(
                    args.from_currency, args.to_currency
                    )
                print(
                    f"Курс {args.from_currency}→{args.to_currency}: "
                    f"{rate:.8f} (обновлено: {updated_at})"
                    )

            elif args.command == "update-rates":
                count, with_errors, last_refresh = usecases.refresh_rates()

                if with_errors:
                    print("Update completed with errors.")
                else:
                    print(f"Update successful. Total rates updated: {count}. Last refresh: {last_refresh}")

            elif args.command == "show-rates":
                rates = usecases.show_rates(args.currency, args.top)

                pairs = rates.get("pairs", {})

                if not pairs:
                    print("Локальный кеш курсов пуст. Выполните 'update-rates', чтобы загрузить данные.")
                    continue

                print(f"Rates from cache (updated at {rates['last_refresh']}):")
                for pair, data in pairs.items():
                    print(f"{pair}: {data['rate']}")

        except SystemExit:
            continue
        except CurrencyNotFoundError as e:
            print(f"Неизвестная валюта: {e}")
        except InsufficientFundsError as e:
            print(e)
        except ApiRequestError as e:
            print(f"Ошибка получения курса: {e}")
        except ValueError as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()