import argparse
import shlex

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

    print("ValutaTrade Hub. Введите команду или exit для выхода.")

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