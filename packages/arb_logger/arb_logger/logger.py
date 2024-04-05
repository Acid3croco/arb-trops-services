import os
import sys
import json
import time
import inspect
import logging
import traceback
import logging.handlers

from pathlib import Path
from typing import Optional
from dataclasses import fields
from collections import defaultdict
from arb_logger.alert_message import AlertMessage

import coloredlogs

from redis import Redis


def get_redis_log_client() -> Optional[Redis]:
    # Will be replaced by another Redis client prolly
    try:
        redis_client = Redis(host='localhost',
                             port=6379,
                             db=0,
                             decode_responses=True)
        success = redis_client.ping()
    except Exception as e:
        raise Exception('Could not connect to Redis') from e

    if not success:
        raise Exception('Could not ping Redis')

    return redis_client


def get_redis_log_key(name: str):
    return f'logs:{name}'


class RedisHandler(logging.Handler):
    THROTTLE_TIME = 60

    def __init__(self, redis_client, redis_key):
        super().__init__()
        self.redis_client: Redis = redis_client
        self.redis_key = redis_key

        self.alert_fields = {f.name for f in fields(AlertMessage)}

        self.last_message_ts = defaultdict(int)

    def _throttle(self, record: logging.LogRecord):
        # Throttle alerts
        msg_hash = hash(record.msg)
        curr_time = int(time.time())

        throttle = False
        if (prev_time := self.last_message_ts.get(
                msg_hash, 0)) and curr_time - prev_time < self.THROTTLE_TIME:
            throttle = True

        self.last_message_ts[msg_hash] = curr_time
        return throttle

    def emit(self, record: logging.LogRecord):
        try:
            # Check if the message is the same as the last one
            # to avoid spamming the redis channel
            if self._throttle(record):
                return

            record_dict = AlertMessage.log_record_to_dict(record)
            #! split : to get the stream name being 'logs' for grafana
            self.redis_client.xadd(self.redis_key.split(':')[0], record_dict)
            self.redis_client.publish(self.redis_key,
                                      json.dumps(record_dict,
                                                 separators=(',', ':'),
                                                 default=str))  # Add this line
        except Exception:
            self.handleError(record)


STDOUT_LEVEL_NUM = 25
logging.addLevelName(STDOUT_LEVEL_NUM, 'STDOUT')


def stdout(self, message, *args, **kwargs):
    if self.isEnabledFor(STDOUT_LEVEL_NUM):
        self._log(STDOUT_LEVEL_NUM, message, args, **kwargs)


logging.Logger.stdout = stdout  # type: ignore


class LoggerStdout:

    def __init__(self, logger):
        self.logger = logger
        self.stdout = sys.stdout

    def write(self, message):
        if message.rstrip() != '':
            self.logger.stdout('\n' + message.rstrip())

    def flush(self):
        self.stdout.flush()

    def isatty(self):
        return self.stdout.isatty()


def get_logger_name():
    # Get the name of the calling module
    name = inspect.getmodule(
        inspect.currentframe().f_back).__name__  # type: ignore
    if name in ('__main__', '__init__', None):
        raise ValueError(
            'Please provide an explicit name for the logger when called from __main__ or __init__.'
        )

    return name


def get_logger(
        name,
        level: int = logging.DEBUG,
        path: Optional[Path] = None,
        log_in_file: bool = True,
        short: bool = False,
        redis_handler: bool = False,  # type: ignore
        custom_redis_client: Optional[Redis] = None):

    name = name or get_logger_name()
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(level)
        logger.propagate = False

        # Set up the custom formatter
        fmt = '%(asctime)s [%(levelname)s] %(name)s - %(message)s - (%(filename)s:%(lineno)d)'
        formatter = logging.Formatter(fmt)

        # Set up coloredlogs with the custom formatter
        coloredlogs.install(level=level,
                            logger=logger,
                            fmt=fmt,
                            milliseconds=True)

        # Set up RedisHandler
        if redis_handler:
            redis_client = custom_redis_client or get_redis_log_client()
            redis_key = get_redis_log_key(name)
            redis_handler: logging.Handler = RedisHandler(
                redis_client, redis_key)
            redis_handler.setLevel(logging.ERROR)
            redis_handler.setFormatter(formatter)
            logger.addHandler(redis_handler)

        # Set up FileHandler
        if log_in_file:
            log_dir = path or Path(os.environ.get('ARB_LOGS_PATH', 'logs'))
            log_dir.mkdir(parents=True, exist_ok=True)

            # Get the rootname of the calling module/logger name
            # use it as the log filename to regroup multiple sublogger
            # under the same file
            _filename = name.split('.')[0]
            if short:
                filename = f'{_filename}.log'
            else:
                pid = os.getpid()
                filename = f'{_filename}.{pid}.log'

            file_handler = logging.handlers.TimedRotatingFileHandler(
                log_dir / filename,
                when='midnight',
                interval=1,
                backupCount=3,
                utc=True)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Log uncaught exceptions using sys.excepthook
        def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
            if exc_type is KeyboardInterrupt:
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            logger.critical(''.join(
                traceback.format_exception(exc_type, exc_value,
                                           exc_traceback)))

        #? DISABLED FOR NOW
        # Redirect stdout to logger
        # sys.stdout = LoggerStdout(logger)
        sys.excepthook = log_uncaught_exceptions

    return logger
