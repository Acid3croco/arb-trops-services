import json
import time

from pathlib import Path
from threading import Thread

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
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, config_file: Path):
        if self.__initialized:
            return
        self.__initialized = True
        self.config_file = config_file
        self.config_data = {}
        self.load_config()

        Thread(target=self.watch_config, daemon=True).start()

    def load_config(self):
        LOGGER.info(f'Loading config from {self.config_file}')
        with open(self.config_file, "r") as f:
            self.config_data = json.load(f)
            LOGGER.info(f'Config loaded: {self.config_data}')

    def watch_config(self):
        LOGGER.info('Watching config file for changes')
        self._observer = Observer()
        event_handler = ConfigFileHandler(self.load_config)
        self._observer.schedule(event_handler,
                                str(self.config_file.parent),
                                recursive=False)
        self._observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._observer.stop()

        self._observer.join()

    def stop(self):
        if hasattr(self, '_observer') and self._observer.is_alive():
            self._observer.stop()
            self._observer.join()


def get_config(config_file: Path) -> Config:
    config = Config(config_file)
    return config
