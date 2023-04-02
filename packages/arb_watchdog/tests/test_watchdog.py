import os
import json
import tempfile
import unittest

from pathlib import Path
from datetime import datetime

from fakeredis import FakeRedis

from arb_watchdog.process_data import ProcessData
from arb_watchdog.config import Config, get_config
from arb_watchdog.process_watcher import ProcessWatcher


class TestArbWatchdog(unittest.TestCase):

    def setUp(self):
        self.test_redis = FakeRedis(decode_responses=True)

        self.config_file = Path(tempfile.NamedTemporaryFile(delete=False).name)
        self.config_data = {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'interval': 60,
            'processes': ['fake_process', 'another_fake_process']
        }

        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f)

        self.config_obj = get_config(self.config_file)

    def tearDown(self):
        self.config_obj.stop()
        os.unlink(self.config_file)

    def test_config(self):
        config = Config(self.config_file)
        self.assertEqual(config.config_data, self.config_data)

        updated_config_data = self.config_data.copy()
        updated_config_data['interval'] = 30

        with open(self.config_file, 'w') as f:
            json.dump(updated_config_data, f)

        config.load_config()
        self.assertEqual(config.config_data, updated_config_data)

        self.config_data['interval'] = 30
        config = get_config(self.config_file)
        self.assertEqual(config.config_data, self.config_data)

    def test_process_data(self):
        # Test default values
        name = 'test_process'
        process_data = ProcessData(name)
        self.assertEqual(process_data.name, name)
        self.assertIsNone(process_data.pid)
        self.assertEqual(process_data.status, 'DOWN')
        self.assertIsNotNone(process_data.last_status_change)
        self.assertIsInstance(process_data.last_status_change, datetime)

        # Test custom values
        last_date = datetime.now()
        process_data = ProcessData(name='test_process',
                                   pid=12345,
                                   status='UP',
                                   last_status_change=last_date)
        self.assertEqual(process_data.name, 'test_process')
        self.assertEqual(process_data.pid, 12345)
        self.assertEqual(process_data.status, 'UP')
        self.assertEqual(process_data.last_status_change, last_date)

    def test_process_watcher(self):
        process_watcher = ProcessWatcher(config_file=self.config_file,
                                         redis_client=self.test_redis)

        # Testing get_process_list
        process_list = process_watcher.get_process_list()
        self.assertEqual(len(process_list), 2)
        self.assertIn('fake_process', process_list)
        self.assertIn('another_fake_process', process_list)

        # Add process_data to fake redis
        for process_name in process_list:
            process_data = ProcessData(name=process_name,
                                       pid=12345,
                                       status='UP')
            process_watcher.update_process_data(process_data)

        # Testing get_process_data of a process that DOESNT exists
        process_name = 'unknow_fake_process'
        process_data = process_watcher.get_process_data(process_name)
        self.assertIsNone(process_data)

        # Testing get_process_data of a process that exists
        process_name = 'fake_process'
        process_data = process_watcher.get_process_data(process_name)
        self.assertIsNotNone(process_data)
        self.assertEqual(process_data.name, process_name)
        self.assertEqual(process_data.pid, 12345)
        self.assertEqual(process_data.status, 'UP')

        # Testing update_process_data
        process_data.status = 'DOWN'
        process_watcher.update_process_data(process_data)

        # Verifying that the process data was updated correctly
        updated_process_data = process_watcher.get_process_data(process_name)
        self.assertEqual(process_data, updated_process_data)
