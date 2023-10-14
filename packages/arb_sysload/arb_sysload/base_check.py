from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

from arb_logger.logger import get_logger

from arb_sysload.utils import get_sysload_redis


class CheckStatus(Enum):
    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"
    RUNNING = "RUNNING"
    FAILED = "FAILED"

    def __str__(self):
        return self.value


class BaseCheck(ABC):
    INTERVAL = 60  # Default: run every minute

    def __init__(self):
        self.logger = get_logger(f'arb_sysload.{self.__class__.__name__}')

        self.name = self.__class__.__name__
        self.last_run = None
        self.status = None
        self.message = None
        self.user_status = None

        self.redis = get_sysload_redis()

    @property
    def check_key(self):
        return f'arb_sysload:{self.name}'

    @abstractmethod
    def run(self):
        """
        Execute the check.
        Should call one of the following methods: success, warning, error
        """
        pass

    def execute(self):
        self.last_run = datetime.now()
        self.status = CheckStatus.RUNNING
        self.message = None
        self._save()
        try:
            self.run()
            # if the check status is running at the end of the run method, it means it didn't call any of the
            # success/warning/error methods, so we can assume it's successful
            if self.status is CheckStatus.RUNNING:
                self.success()
        except Exception as e:
            self.failed(str(e))
        self.last_run = datetime.now()
        self._save()

        return self.status

    def success(self, message=None):
        self.status = CheckStatus.OK
        self.message = message or "All good!"
        self.logger.info(self.message)

    def warning(self, message):
        self.status = CheckStatus.WARNING
        self.message = message
        self.logger.warning(message)

    def error(self, message):
        self.status = CheckStatus.ERROR
        self.message = message
        self.logger.error(message)

    def failed(self, message):
        self.status = CheckStatus.FAILED
        self.message = message
        self.logger.critical(message)

    def _save(self):
        data = self._to_dict()
        self.redis.hset(self.check_key, mapping=data)

    def _to_dict(self):
        # cant let None
        return {
            "name": self.name,
            "last_run":
            self.last_run.isoformat() if self.last_run else f"{self.last_run}",
            "status":
            self.status.name if self.status else CheckStatus.UNKNOWN.name,
            "message": self.message or '',
            # "user_status": self.user_status.name if self.user_status else None
        }
