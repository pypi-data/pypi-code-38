
from unittest import TestCase
import os
import logging
from lando.testutil import write_temp_return_filename
from lando.worker.config import WorkerConfig
from lando.exceptions import InvalidConfigException

GOOD_CONFIG = """
host: 10.109.253.74
username: worker
password: workerpass
queue_name: task-queue
cwl_base_command: 
- cwltoil
cwl_post_process_command: 
- rm 
- bad.data
commands:
  stage_data_command: ["python", "-m", "lando_util.stagedata"]
  organize_output_command: ["python", "-m", "lando_util.organize_project"]
  save_output_command: ["python", "-m", "lando_util.upload"]
"""

# missing queuename field
BAD_CONFIG = """
host: 10.109.253.74
username: worker
password: workerpass
"""


class TestWorkerConfig(TestCase):
    def test_good_config(self):
        filename = write_temp_return_filename(GOOD_CONFIG)
        config = WorkerConfig(filename)
        os.unlink(filename)
        work_queue_config = config.work_queue_config
        self.assertEqual("10.109.253.74", work_queue_config.host)
        self.assertEqual("worker", work_queue_config.username)
        self.assertEqual("workerpass", work_queue_config.password)
        self.assertEqual("task-queue", work_queue_config.queue_name)
        self.assertEqual(["cwltoil"], config.cwl_base_command)
        self.assertEqual(['rm', 'bad.data'], config.cwl_post_process_command)
        self.assertEqual(logging.WARNING, config.log_level)

    def test_empty_config(self):
        filename = write_temp_return_filename("")
        with self.assertRaises(InvalidConfigException):
            config = WorkerConfig(filename)
        os.unlink(filename)

    def test_bad_config(self):
        filename = write_temp_return_filename(BAD_CONFIG)
        with self.assertRaises(InvalidConfigException):
            config = WorkerConfig(filename)
        os.unlink(filename)

    def test_log_level(self):
        filename = write_temp_return_filename('{}\nlog_level: INFO'.format(GOOD_CONFIG))
        config = WorkerConfig(filename)
        os.unlink(filename)
        self.assertEqual('INFO', config.log_level)
