from unittest import TestCase
from lando.k8s.config import create_server_config, InvalidConfigException, ServerConfig
from unittest.mock import patch
import logging

MINIMAL_CONFIG = {
    'work_queue': {
        'host': 'somehost',
        'username': 'lando',
        'password': 'secret',
        'worker_username': 'worker',
        'worker_password': 'secret2',
        'listen_queue': 'lando'
    },
    'cluster_api_settings': {
        'host': 'somehost2',
        'token': 'myToken1',
        'namespace': 'lando-job-runner',
    },
    'bespin_api': {
        'url': 'someurl',
        'token': 'myToken2',
    },
    'data_store_settings': {
        'secret_name': 'ddsclient-secret'
    },
    'run_workflow_settings': {},
    'record_output_project_settings': {
        'service_account_name': 'annotation-writer-sa',
    },
}

FULL_CONFIG = {
    'log_level': logging.DEBUG,
    'work_queue': {
        'host': 'somehost',
        'username': 'lando',
        'password': 'secret',
        'worker_username': 'worker',
        'worker_password': 'secret2',
        'listen_queue': 'lando'
    },
    'cluster_api_settings': {
        'host': 'somehost2',
        'token': 'myToken1',
        'namespace': 'lando-job-runner',
        'verify_ssl': False,
    },
    'bespin_api': {
        'url': 'someurl',
        'token': 'myToken2',
    },
    'data_store_settings': {
        'secret_name': 'ddsclient-secret'
    },
    'run_workflow_settings': {
        'system_data_volume': {
            'mount_path': '/system/data',
            'volume_claim_name': 'system-data',
        }
    },
    'record_output_project_settings': {
        'service_account_name': 'annotation-writer-sa',
    },
    'storage_class_name': 'gluster',
    'base_stage_data_volume_size_in_g': 3
}


class TestServerConfig(TestCase):
    @patch('lando.k8s.config.ServerConfig')
    @patch('builtins.open')
    @patch('lando.k8s.config.yaml')
    def test_create_server_config(self, mock_yaml, mock_open, mock_server_config):
        mock_yaml.safe_load.return_value = {"logging": "INFO"}
        server_config = create_server_config('somefile')
        self.assertEqual(server_config, mock_server_config.return_value)
        mock_server_config.assert_called_with({"logging": "INFO"})

        mock_yaml.safe_load.return_value = {}
        with self.assertRaises(InvalidConfigException):
            create_server_config('somefile')

    def test_minimal_config(self):
        config = ServerConfig(MINIMAL_CONFIG)
        self.assertEqual(config.log_level, logging.WARN)
        self.assertIsNotNone(config.work_queue_config)

        self.assertEqual(config.cluster_api_settings.host, 'somehost2')
        self.assertEqual(config.cluster_api_settings.token, 'myToken1')
        self.assertEqual(config.cluster_api_settings.namespace, 'lando-job-runner')
        self.assertEqual(config.cluster_api_settings.verify_ssl, True)

        self.assertIsNotNone(config.bespin_api_settings)
        self.assertEqual(config.data_store_settings.secret_name, 'ddsclient-secret')
        self.assertEqual(config.run_workflow_settings.system_data_volume, None)
        self.assertEqual(config.record_output_project_settings.service_account_name, 'annotation-writer-sa')

        self.assertEqual(config.storage_class_name, None)
        self.assertEqual(config.base_stage_data_volume_size_in_g, 1)

    def test_optional_config(self):
        config = ServerConfig(FULL_CONFIG)
        self.assertEqual(config.log_level, logging.DEBUG)
        self.assertEqual(config.run_workflow_settings.system_data_volume.mount_path, '/system/data')
        self.assertEqual(config.run_workflow_settings.system_data_volume.volume_claim_name, 'system-data')
        self.assertEqual(config.cluster_api_settings.verify_ssl, False)
        self.assertEqual(config.base_stage_data_volume_size_in_g, 3)
