import os
import sys
import json
import inspect
import logging
import traceback

from pathlib import Path

import coloredlogs

from redis import Redis


def get_redis_log_client() -> Redis:
    # Will be replaced by another Redis client prolly
    return Redis(host='localhost', port=6379, db=0, decode_responses=True)


class RedisHandler(logging.Handler):

    def __init__(self, redis_client, stream_key):
        super().__init__()
        self.redis_client: Redis = redis_client
        self.stream_key = stream_key

    def emit(self, record):
        try:
            record_dict = {
                k: v
                for k, v in record.__dict__.items()
                if k != 'args' and not k.startswith('_') and v is not None
            }
            self.redis_client.xadd(self.stream_key, record_dict)
            self.redis_client.publish(self.stream_key,
                                      json.dumps(record_dict))  # Add this line
        except Exception:
            self.handleError(record)


STDOUT_LEVEL_NUM = 25
logging.addLevelName(STDOUT_LEVEL_NUM, 'STDOUT')


def stdout(self, message, *args, **kwargs):
    if self.isEnabledFor(STDOUT_LEVEL_NUM):
        self._log(STDOUT_LEVEL_NUM, message, args, **kwargs)


logging.Logger.stdout = stdout


class LoggerStdout:

    def __init__(self, logger):
        self.logger = logger
        self.stdout = sys.stdout

    def write(self, message):
        if message.rstrip() != '':
            self.logger.stdout(message.rstrip())

    def flush(self):
        self.stdout.flush()

    def isatty(self):
        return self.stdout.isatty()


def get_logger_name():
    # Get the name of the calling module
    name = inspect.getmodule(inspect.currentframe().f_back).__name__
    if name in ('__main__', '__init__'):
        raise ValueError(
            'Please provide an explicit name for the logger when called from __main__ or __init__.'
        )

    return name


def get_logger(name: str = None,
               level: int = logging.DEBUG,
               path: Path = None,
               log_in_file: bool = True,
               short: bool = False):
    logger = logging.getLogger(name or get_logger_name())

    if not logger.hasHandlers():
        logger.setLevel(level)
        logger.propagate = False

        # Set up the custom formatter
        fmt = '%(asctime)s [%(levelname)s] %(name)s - %(message)s - (%(filename)s:%(lineno)d)'
        formatter = logging.Formatter(fmt)

        # Set up coloredlogs with the custom formatter
        coloredlogs.install(level=level, logger=logger, fmt=fmt)

        # Set up RedisHandler
        redis_client = get_redis_log_client()
        stream_key = f'logs:{name}'
        redis_handler = RedisHandler(redis_client, stream_key)
        redis_handler.setLevel(logging.WARNING)
        redis_handler.setFormatter(formatter)
        logger.addHandler(redis_handler)

        # Set up FileHandler
        if log_in_file:
            log_dir = path or Path(os.environ.get('ARB_LOGS_PATH', 'logs'))
            log_dir.mkdir(parents=True, exist_ok=True)

            if short:
                filename = f'{name}.log'
            else:
                pid = os.getpid()
                filename = f'{name}.{pid}.log'
            file_handler = logging.FileHandler(log_dir / filename)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Log uncaught exceptions using sys.excepthook
        def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
            logger.critical(''.join(
                traceback.format_exception(exc_type, exc_value,
                                           exc_traceback)))

        sys.stdout = LoggerStdout(logger)
        sys.excepthook = log_uncaught_exceptions

    return logger
