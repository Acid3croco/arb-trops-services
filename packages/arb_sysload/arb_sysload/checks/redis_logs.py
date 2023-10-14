from redis import Redis

from arb_sysload.base_check import BaseCheck


class RedisLogsCheck(BaseCheck):

    def run(self):
        redis = Redis(host='localhost', port=6379, decode_responses=True)
        length = redis.xlen("logs")
        if length > 1000:  # Example threshold
            message = f"Redis logs stream length is {length}, which is above the threshold."
            self.error(message)
        else:
            self.success(f"Redis logs stream length is {length}")
