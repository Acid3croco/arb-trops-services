import json
import logging
import platform

from arb_logger.log_message import LogMessage
from arb_logger.logger import get_logger, get_redis_log_client, get_redis_log_key

if platform.system() == 'Darwin':
    import pync

LOGGER = get_logger('RedisLogSubscriber', short=True)


class RedisLogSubscriber:

    def __init__(self):
        self.redis_client = get_redis_log_client()

    def listen(self):
        self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
        pattern = get_redis_log_key('*')
        self.pubsub.psubscribe(pattern)

        for message in self.pubsub.listen():
            if message['type'] == 'pmessage':
                if message['channel'] == 'logs:RedisLogSubscriber':
                    # Prevent recursive logging of RedisLogSubscriber's messages
                    continue
                try:
                    record_dict = json.loads(message['data'])
                    log_message = LogMessage.from_dict(record_dict)
                    self.process_log_message(log_message)
                except Exception as e:
                    LOGGER.exception(
                        f"Error while processing log message: {e}")

    def process_log_message(self, log_message: LogMessage):
        log_record = logging.LogRecord(name=log_message.name,
                                       level=log_message.levelno,
                                       pathname=log_message.pathname,
                                       lineno=log_message.lineno,
                                       msg=log_message.msg,
                                       args=log_message.args,
                                       exc_info=log_message.exc_info,
                                       func=log_message.funcName)
        LOGGER.handle(log_record)

        if log_message.levelno >= logging.ERROR:
            """
            make this async
            """
            self.send_macos_notification(log_message)

    def send_macos_notification(self, log_message: LogMessage):
        if platform.system() == 'Darwin':
            title = f"{log_message.levelname} - {log_message.name}"
            subtitle = f"{log_message.filename}:{log_message.lineno}"
            message = log_message.msg
            pync.notify(message, title=title, subtitle=subtitle, wait=True)


def main():
    LOGGER.info('Starting RedisLogSubscriber')
    log_subscriber = RedisLogSubscriber()
    LOGGER.info('Listening for log messages...')
    print('')
    log_subscriber.listen()


if __name__ == '__main__':
    main()
