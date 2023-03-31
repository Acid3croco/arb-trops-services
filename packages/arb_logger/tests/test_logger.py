import unittest

from arb_logger.log_message import LogMessage
from arb_logger.redis_log_client import RedisLogSubscriber
from arb_logger.logger import get_logger, STDOUT_LEVEL_NUM


class TestLogger(unittest.TestCase):

    def test_get_logger(self):
        logger = get_logger('test_get_logger')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'test_get_logger')

    def test_stdout_level_num(self):
        self.assertEqual(STDOUT_LEVEL_NUM, 25)

    def test_log_message(self):
        log_message = LogMessage(name='test',
                                 levelname='INFO',
                                 msg='Test message')
        self.assertEqual(log_message.name, 'test')
        self.assertEqual(log_message.levelname, 'INFO')
        self.assertEqual(log_message.msg, 'Test message')

    def test_redis_log_subscriber(self):
        subscriber = RedisLogSubscriber()
        self.assertIsNotNone(subscriber)
        self.assertIsNotNone(subscriber.redis_client)


if __name__ == '__main__':
    unittest.main()
