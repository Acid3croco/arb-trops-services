import os

from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser

from redis import Redis
from tabulate import tabulate
from colorama import init, Fore

from arb_watchdog.config import get_config
from arb_watchdog.process_data import ProcessData


class ProcessWatchdogCLI:

    def __init__(self, config_file: Path):
        self._config = get_config(config_file)
        redis_host = self.config.get('redis_host')
        redis_port = self.config.get('redis_port')

        self.redis = Redis(host=redis_host or 'localhost',
                           port=redis_port or 6379,
                           decode_responses=True)

    @property
    def config(self):
        return self._config.config_data

    def get_process_list(self):
        return self.config.get('processes', [])

    def get_process_info(self, process_name):
        key = f'arb_watchdog:{process_name}'
        data = self.redis.hgetall(key)
        return ProcessData(**data)

    def _get_process_last_status_change(self, process_data: ProcessData):
        try:
            last_change = process_data.last_status_change
            if last_change.date() == datetime.today().date():
                return last_change.strftime('%H:%M:%S')
            return last_change.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return 'N/A'

    def display_process_info(self):
        process_list = self.get_process_list()
        table_data = []

        for process_name in process_list:
            process_data = self.get_process_info(process_name)

            if process_data:

                status_colored = process_data.status

                if process_data.status == 'UP':
                    status_colored = Fore.GREEN + status_colored + Fore.RESET
                elif process_data.status == 'DOWN':
                    status_colored = Fore.RED + status_colored + Fore.RESET
                else:
                    status_colored = Fore.LIGHTBLACK_EX + status_colored + Fore.RESET

                last_status_change = self._get_process_last_status_change(
                    process_data)
                table_data.append([
                    process_data.name,
                    status_colored,
                    process_data.pid,
                    last_status_change,
                ])
        headers = ['Name', 'Status', 'PID', 'Last Status Change']
        table_data.sort(key=lambda x: x[0].lower())
        print('\n' + tabulate(table_data, headers=headers, tablefmt='grid'))


def main():
    default_path = (os.getenv('ARB_CONFIGS_PATH', '.') +
                    '/arb_watchdog_config.json')

    parser = ArgumentParser(description='Process Watchdog CLI')
    parser.add_argument('-f',
                        '--config-file',
                        type=Path,
                        default=default_path,
                        help='Path to the configuration file')
    args = parser.parse_args()

    cli = ProcessWatchdogCLI(config_file=args.config_file)
    cli.display_process_info()


if __name__ == '__main__':
    main()
