import json
import shutil
import logging

from pathlib import Path
from unittest.mock import patch
from unittest import TestCase, mock

from redis import Redis
from fakeredis import FakeRedis

from arb_logger.alert_message import AlertMessage
from arb_logger.logger import get_logger, RedisHandler, get_redis_log_key


class TestAlertMessage(TestCase):

    def test_from_dict(self):
        record_dict = {
            "name": "test_name",
            "msg": "test message",
            "levelno": 40,
            "levelname": "ERROR",
            "pathname": "test_path",
            "lineno": 42,
            "extra_data": "extra_value"
        }

        log_message = AlertMessage.from_dict(record_dict)
        self.assertEqual(log_message.name, "test_name")
        self.assertEqual(log_message.msg, "test message")
        self.assertEqual(log_message.extra["extra_data"], "extra_value")


class TestLogger(TestCase):

    def setUp(self):
        self.custom_logs_path = Path("custom_logs")
        self.custom_logs_path.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.custom_logs_path)

    def test_get_logger(self):
        logger = get_logger("test_logger")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.DEBUG)

    def test_redis_handler(self):
        redis_client = Redis()
        redis_key = get_redis_log_key("test_logger")

        handler = RedisHandler(redis_client, redis_key)
        self.assertIsInstance(handler, RedisHandler)

    @mock.patch("arb_logger.logger.Redis.publish")
    def test_redis_handler_emit(self, mock_publish):
        logger = get_logger("test_logger")
        message = "Test message"
        logger.error(message)

        _, args, _ = mock_publish.mock_calls[0]
        channel, msg = args
        msg_dict = json.loads(msg)

        self.assertEqual(channel, "logs:test_logger")
        self.assertEqual(msg_dict["msg"], message)

    def test_get_logger_with_arguments(self):
        logger = get_logger(name="test_logger_2",
                            level=logging.INFO,
                            log_in_file=False,
                            short=True,
                            redis_handler=False)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger_2")
        self.assertEqual(logger.level, logging.INFO)

    @patch("arb_logger.logger.Path.mkdir")
    def test_get_logger_with_path(self, mock_mkdir):
        logger = get_logger(name="test_logger_3", path=self.custom_logs_path)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger_3")
        mock_mkdir.assert_called_once()

    @patch("arb_logger.logger.logging.Logger._log")
    def test_stdout(self, mock_log):
        logger = get_logger("test_logger")
        message = "Test STDOUT message"
        logger.stdout(message)

        mock_log.assert_called_once_with(25, message, ())


class TestRedisLogger(TestCase):

    def setUp(self):
        self.redis_client = FakeRedis(decode_responses=True)

    def test_redis_handler(self):
        logger = get_logger(name="test_redis_logger",
                            custom_redis_client=self.redis_client)
        message = "Test Redis message"
        logger.warning(message)

        redis_key = get_redis_log_key(logger.name)
        #! split : to get the stream name being 'logs' for grafana - also in logger.py:39
        messages = self.redis_client.xrange(redis_key.split(':')[0], count=1)

        self.assertEqual(len(messages), 1)
        # messages is a list of tuples, the first element is the message id, the second is the message itself
        self.assertEqual(len(messages[0]), 2)

        log_data = messages[0][1]
        self.assertEqual(log_data["msg"], message)

    def test_redis_log_level_filter(self):
        logger = get_logger(name="test_redis_log_level_filter",
                            custom_redis_client=self.redis_client)
        message1 = "Test Redis INFO message"
        logger.info(message1)

        message2 = "Test Redis WARNING message"
        logger.warning(message2)

        redis_key = get_redis_log_key(logger.name)
        messages = self.redis_client.xrange(redis_key.split(':')[0], count=2)

        self.assertEqual(len(messages), 1)
        log_data = messages[0][1]
        self.assertEqual(log_data["msg"], message2)

    def test_redis_custom_extra_fields(self):
        logger = get_logger(name="test_redis_custom_extra_fields",
                            custom_redis_client=self.redis_client)
        extra = {"key1": "value1", "key2": "value2"}
        message = "Test Redis message with extra fields"
        logger.warning(message, extra=extra)

        redis_key = get_redis_log_key(logger.name)
        messages = self.redis_client.xrange(redis_key.split(':')[0], count=1)

        self.assertEqual(len(messages), 1)
        log_data = messages[0][1]
        self.assertEqual(log_data["msg"], message)

        for key, value in extra.items():
            self.assertEqual(log_data[key], value)
