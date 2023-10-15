from redis import Redis

from arb_sysload.base_check import BaseCheck


class RedisLogsCheck(BaseCheck):
    REDIS_LOGS_SIZE_THRESHOLD = 30000

    def run(self):
        redis = Redis(host='localhost', port=6379, decode_responses=True)
        length = redis.xlen("logs")
        if length > self.REDIS_LOGS_SIZE_THRESHOLD:  # Example threshold
            message = f"Redis logs stream length is {length}, which is above the threshold of {self.REDIS_LOGS_SIZE_THRESHOLD}"
            self.error(message)
        else:
            self.success(
                f"Redis logs stream length is {length}/{self.REDIS_LOGS_SIZE_THRESHOLD}"
            )
