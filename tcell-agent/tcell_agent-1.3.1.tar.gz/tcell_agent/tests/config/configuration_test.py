import unittest

from tcell_agent.config.configuration import TCellAgentConfiguration


class TcellAgentConfigurationTest(unittest.TestCase):
    def test_setting_max_data_ex_db_records_per_request(self):
        data_exposure_config_json = {
            "version": 1,
            "applications": [
                {
                    "name": "name",
                    "app_id": "app_id",
                    "api_key": "api_key",
                    "data_exposure": {
                        "max_data_ex_db_records_per_request": 100
                    }
                }
            ]
        }
        configuration = TCellAgentConfiguration()
        configuration.read_config(data_exposure_config_json)
        self.assertEqual(configuration.max_data_ex_db_records_per_request, 100)

    def test_default_allow_payloads(self):
        simple_config_json = {
            "version": 1,
            "applications": [
                {
                    "name": "name",
                    "app_id": "app_id",
                    "api_key": "api_key"
                }
            ]
        }
        configuration = TCellAgentConfiguration()
        configuration.read_config(simple_config_json)
        self.assertTrue(configuration.allow_payloads)
