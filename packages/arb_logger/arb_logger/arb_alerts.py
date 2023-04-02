import json
import logging
import platform

from arb_logger.alert_message import AlertMessage
from arb_logger.logger import get_logger, get_redis_log_client, get_redis_log_key

if platform.system() == 'Darwin':
    import pync

LOGGER = get_logger('arb_alerts', short=True, redis_handler=False)


class ArbAlerts:

    def __init__(self):
        self.redis_client = get_redis_log_client()

    def listen(self):
        self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
        pattern = get_redis_log_key('*')
        self.pubsub.psubscribe(pattern)

        for message in self.pubsub.listen():
            if message['type'] == 'pmessage':
                if message['channel'] == 'logs:arb_alerts':
                    # Prevent recursive logging of arb_alerts's messages
                    continue
                try:
                    record_dict = json.loads(message['data'])
                    log_message = AlertMessage.from_dict(record_dict)
                    self.log_alert_message(log_message)
                except Exception as e:
                    LOGGER.exception(
                        f"Error while processing log message: {e}")

    def log_alert_message(self, alert_message: AlertMessage):
        # Convert back AlertMessage to LogRecord to be handled by local logger easily
        msg = alert_message.msg
        if alert_message.extra:
            msg += f" {str(alert_message.extra)}"
        log_record = logging.LogRecord(name=alert_message.name,
                                       level=alert_message.levelno,
                                       pathname=alert_message.pathname,
                                       lineno=alert_message.lineno,
                                       msg=msg,
                                       func=alert_message.funcName,
                                       args=None,
                                       exc_info=None)
        LOGGER.handle(log_record)

        if alert_message.levelno >= logging.ERROR:
            """
            make this async
            """
            self.send_macos_notification(alert_message)

    def send_macos_notification(self, log_message: AlertMessage):
        if platform.system() == 'Darwin':
            title = f"{log_message.levelname} - {log_message.name}"
            subtitle = f"{log_message.filename}:{log_message.lineno}"
            message = log_message.msg
            pync.notify(message, title=title, subtitle=subtitle, wait=True)


def main():
    LOGGER.info('Starting arb_alerts')
    arb_alerts = ArbAlerts()
    LOGGER.info('Listening for log messages...')
    arb_alerts.listen()


if __name__ == '__main__':
    main()
