from unittest import TestCase
import os
import logging
from lando.testutil import write_temp_return_filename
from lando.server.config import ServerConfig
from lando.exceptions import InvalidConfigException
from unittest.mock import Mock

GOOD_CONFIG = """
work_queue:
  host: 10.109.253.74
  username: lando
  password: odnal
  worker_username: lobot
  worker_password: tobol
  listen_queue: lando

{}

cloud_settings:
  auth_url: http://10.109.252.9:5000/v3
  username: jpb67
  user_domain_name: Default
  project_name: jpb67
  project_domain_name: Default
  password: secret

bespin_api:
  url: http://localhost:8000/api
  token: 10498124091240e
  
commands:
  stage_data_command: ["python", "-m", "lando_util.stagedata"]
  organize_output_command: ["python", "-m", "lando_util.organize_project"]
  save_output_command: ["python", "-m", "lando_util.upload"]
"""


class TestServerConfig(TestCase):
    def test_good_config(self):
        filename = write_temp_return_filename(GOOD_CONFIG.format(""))
        config = ServerConfig(filename)
        os.unlink(filename)
        self.assertEqual(False, config.fake_cloud_service)

        self.assertEqual("10.109.253.74", config.work_queue_config.host)
        self.assertEqual("lando", config.work_queue_config.listen_queue)

        self.assertEqual("http://10.109.252.9:5000/v3", config.cloud_settings.auth_url)
        self.assertEqual("jpb67", config.cloud_settings.username)

        self.assertEqual("http://localhost:8000/api", config.bespin_api_settings.url)
        self.assertEqual("10498124091240e", config.bespin_api_settings.token)
        self.assertEqual(logging.WARNING, config.log_level)

    def test_good_config_with_fake_cloud_service(self):
        config_data = GOOD_CONFIG.format("") + "\nfake_cloud_service: True"
        filename = write_temp_return_filename(config_data)
        config = ServerConfig(filename)
        os.unlink(filename)
        self.assertEqual(True, config.fake_cloud_service)

    def test_empty_config_file(self):
        filename = write_temp_return_filename('')
        with self.assertRaises(InvalidConfigException):
            config = ServerConfig(filename)
        os.unlink(filename)

    def test_bogus_config_file(self):
        filename = write_temp_return_filename('stuff: one')
        with self.assertRaises(InvalidConfigException):
            config = ServerConfig(filename)
        os.unlink(filename)

    def test_make_worker_config_yml(self):
        filename = write_temp_return_filename(GOOD_CONFIG.format("log_level: DEBUG"))
        config = ServerConfig(filename)
        os.unlink(filename)
        expected = """
commands:
  organize_output_command:
  - python
  - -m
  - lando_util.organize_project
  save_output_command:
  - python
  - -m
  - lando_util.upload
  stage_data_command:
  - python
  - -m
  - lando_util.stagedata
cwl_base_command: null
cwl_post_process_command: null
cwl_pre_process_command: null
host: 10.109.253.74
log_level: DEBUG
password: tobol
queue_name: worker_1
username: lobot
"""
        mock_cwl_command = Mock(base_command=None, post_process_command=None, pre_process_command=None)
        result = config.make_worker_config_yml('worker_1', mock_cwl_command)
        self.assertMultiLineEqual(expected.strip(), result.strip())

    def test_make_worker_config_yml_custom_cwl_base_command(self):
        mock_cwl_command = Mock(
            base_command=['cwltoil','--not-strict'],
            post_process_command=['rm','tmp.data'],
            pre_process_command=[],
        )

        base_command_line = '  cwl_base_command:\n  - "cwltoil"\n  - "--not-strict"'
        post_process_command_line = '  cwl_post_process_command:\n  - "rm"\n  - "tmp.data"'
        lines = '{}\n{}\n'.format(base_command_line, post_process_command_line)
        filename = write_temp_return_filename(GOOD_CONFIG.format(lines))
        config = ServerConfig(filename)
        config.log_level = 'DEBUG'
        os.unlink(filename)
        expected = """
commands:
  organize_output_command:
  - python
  - -m
  - lando_util.organize_project
  save_output_command:
  - python
  - -m
  - lando_util.upload
  stage_data_command:
  - python
  - -m
  - lando_util.stagedata
cwl_base_command:
- cwltoil
- --not-strict
cwl_post_process_command:
- rm
- tmp.data
cwl_pre_process_command: []
host: 10.109.253.74
log_level: DEBUG
password: tobol
queue_name: worker_1
username: lobot
"""
        result = config.make_worker_config_yml('worker_1', mock_cwl_command)
        self.assertMultiLineEqual(expected.strip(), result.strip())

    def test_log_level(self):
        filename = write_temp_return_filename(GOOD_CONFIG.format('log_level: INFO'))
        config = ServerConfig(filename)
        self.assertEqual('INFO', config.log_level)
        os.unlink(filename)

    def test_worker_log_level(self):
        filename = write_temp_return_filename(GOOD_CONFIG.format('log_level: INFO'))
        config = ServerConfig(filename)
        mock_cwl_command = Mock(base_command=None, post_process_command=None, pre_process_command=None)
        worker_config = config.make_worker_config_yml('worker_1', mock_cwl_command)
        self.assertIn('log_level: INFO', worker_config)
        os.unlink(filename)
