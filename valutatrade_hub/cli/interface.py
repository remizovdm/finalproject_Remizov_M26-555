import argparse
import shlex
import json

from valutatrade_hub.core import usecases

from valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError,
    )


def create_parser():
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
    parser = create_parser()

    print("Добро пожаловать в ValutaTrade Hub! Введите необходимую команду или введите 'exit' для выхода.")

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
                count, with_errors = usecases.refresh_rates()

                if with_errors:
                    print("Update completed with errors.")
                else:
                    with open("data/rates.json", "r", encoding="utf-8") as file:
                        rates = json.load(file)

                    print(
                        f"Update successful. Total rates updated: {count}. "
                        f"Last refresh: {rates['last_refresh']}"
                    )

            elif args.command == "show-rates":
                try:
                    with open("data/rates.json", "r", encoding="utf-8") as file:
                        rates = json.load(file)
                except (FileNotFoundError, json.JSONDecodeError):
                    rates = {}

                pairs = rates.get("pairs", {})

                if not pairs:
                    print("Локальный кеш курсов пуст. Выполните 'update-rates', чтобы загрузить данные.")
                    continue

                if args.currency:
                    currency = args.currency.upper()
                    pairs = {
                        pair: data
                        for pair, data in pairs.items()
                        if pair.startswith(currency + "_")
                    }

                if args.currency and not pairs:
                     print(f"Курс для '{currency}' не найден в кеше.")
                     continue

                if args.top is not None:
                    crypto_pairs = {
                        pair: data
                        for pair, data in pairs.items()
                        if pair.split("_")[0] in ("BTC", "ETH")
                    }

                    pairs = dict(
                        sorted(
                            crypto_pairs.items(),
                            key=lambda item: item[1]["rate"],
                            reverse=True
                        )[:args.top]
                    )

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