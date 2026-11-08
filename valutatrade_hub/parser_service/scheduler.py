import time

from valutatrade_hub.parser_service.updater import RatesUpdater


def start_scheduler(interval=300):
    updater = RatesUpdater()
    while True:
        updater.run_update()
        time.sleep(interval)

if __name__ == "__main__":
    start_scheduler()
