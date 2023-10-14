import os
import time
import psutil

from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from argparse import ArgumentParser

from redis import Redis, RedisError

from arb_logger.logger import get_logger
from arb_watchdog.config import get_config
from arb_watchdog.process_data import ProcessData

LOGGER = get_logger(name='arb_watchdog.watcher', redis_handler=False)


def factory(data):

    def _factory_mapper(v):
        if isinstance(v, datetime):
            return v.timestamp()
        return v

    return {k: _factory_mapper(v) for (k, v) in data if v is not None}


def get_redis_client(host='localhost', port=6379) -> Redis:
    host = host or 'localhost'
    port = port or 6379
    redis = Redis(host=host, port=port, db=0, decode_responses=True)

    try:
        redis.ping()
    except RedisError as e:
        LOGGER.error(f'Error while connecting to Redis: {e}')
        raise e
    return redis


class ProcessWatcher:

    def __init__(self, config_file, redis_client=None):
        self.config_obj = get_config(config_file)
        # allow custom redis client (e.g: for testing)
        self.redis = redis_client or get_redis_client(
            host=self.config.get('redis_host'),
            port=self.config.get('redis_port'))

    @property
    def config(self):
        return self.config_obj.config_data

    @staticmethod
    def _get_redis_key(process_name):
        return f'arb_watchdog:{process_name}'

    def get_process_data(self, process_name) -> ProcessData:
        key = self._get_redis_key(process_name)
        data = self.redis.hgetall(key)
        if not data: return
        return ProcessData(**data)

    def get_process_info(self, process_name):
        for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(process.info.get('cmdline') or [])
                if process_name in cmdline:
                    return ProcessData(name=process_name,
                                       pid=process.info['pid'],
                                       status='UP',
                                       cmdline=cmdline)
            except (psutil.NoSuchProcess, psutil.AccessDenied,
                    psutil.ZombieProcess) as e:
                LOGGER.error(f'Error while iterating over processes: {e}')
                continue
        return None

    def update_process_data(self, process_data: ProcessData):
        try:
            key = self._get_redis_key(process_data.name)
            process_data_dict = asdict(process_data, dict_factory=factory)
            self.redis.hset(key, mapping=process_data_dict)

        except RedisError as e:
            LOGGER.error(f'Error while updating process status in Redis: {e}')

    def get_process_list(self):
        processes = self.config.get('processes', [])
        if not processes:
            LOGGER.error('No processes found in config file')
        return processes

    def watch_processes(self):
        LOGGER.info('Starting process watcher')

        while True:
            for process_name in self.get_process_list():
                process_data = self.get_process_info(process_name)
                if process_data is None:
                    process_data = ProcessData(name=process_name)
                if process_data.status == 'DOWN':
                    LOGGER.error(f'Process {process_name} is down')
                self.update_process_data(process_data)
            time.sleep(self.config.get('interval', 60))


def main():
    default_path = (os.getenv('ARB_CONFIGS_PATH', '.') +
                    '/arb_watchdog_config.json')

    parser = ArgumentParser(description='Process Watcher')
    parser.add_argument('-f',
                        '--config-file',
                        type=Path,
                        default=default_path,
                        help='Path to the configuration file')
    args = parser.parse_args()

    LOGGER.info('Starting arb watchdog')
    watcher = ProcessWatcher(config_file=args.config_file)
    watcher.watch_processes()


if __name__ == '__main__':
    main()
