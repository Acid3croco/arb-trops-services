import json
from threading import Thread
import time

from typing import Dict
from pathlib import Path

from watchdog.observers import Observer
from arb_logger.logger import get_logger
from watchdog.events import FileSystemEventHandler

LOGGER = get_logger(name='arb_watchdog.config')


class ConfigFileHandler(FileSystemEventHandler):

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback()


class Config:

    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.config_data = {}
        self.load_config()

    def load_config(self):
        LOGGER.info(f'Loading config from {self.config_file}')
        with open(self.config_file, "r") as f:
            self.config_data = json.load(f)
            LOGGER.info(f'Config loaded: {self.config_data}')

    def watch_config(self):
        LOGGER.info('Watching config file for changes')
        observer = Observer()
        event_handler = ConfigFileHandler(self.load_config)
        observer.schedule(event_handler,
                          str(self.config_file.parent),
                          recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


def get_config(config_file: Path) -> Config:
    config = Config(config_file)
    Thread(target=config.watch_config, daemon=True).start()
    return config
