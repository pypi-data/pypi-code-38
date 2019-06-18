import json
import os
import zlib
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.contrib import StackifyAPM
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.traces import get_transaction


STACKIFY_JSON_FILE = 'stackify.json'

CONFIG = {
    "APPLICATION_NAME": "sample_application",
    "ENVIRONMENT": "production",
    "BASE_DIR": "path/to/application/",
    "CONFIG_FILE": "path/to/{}".format(STACKIFY_JSON_FILE),
}

CONFIG_FILE = {
    "application_name": "sample_application",
    "environment": "production",
    "base_dir": "path/to/application/",
    "config_file": "path/to/{}".format(STACKIFY_JSON_FILE)
}


class GenericIntegrationTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.contrib.setup_logging')
        self.setup_logging.start()
        register._cls_registers = {}

    def tearDown(self):
        control.uninstrument()
        self.setup_logging.stop()

    def test_default_config(self):
        apm = StackifyAPM()

        assert apm.client.config.application_name == "Python Application"
        assert apm.client.config.environment == "Production"
        assert apm.client.config.base_dir
        assert apm.client.config.config_file == STACKIFY_JSON_FILE

    def test_config_values_upper_keys(self):
        apm = StackifyAPM(**CONFIG)

        assert apm.client.config.application_name == CONFIG["APPLICATION_NAME"]
        assert apm.client.config.environment == CONFIG["ENVIRONMENT"]
        assert apm.client.config.base_dir == CONFIG["BASE_DIR"]
        assert apm.client.config.config_file == CONFIG["CONFIG_FILE"]

    def test_config_values_lower_keys(self):
        apm = StackifyAPM(**CONFIG_FILE)

        assert apm.client.config.application_name == CONFIG_FILE["application_name"]
        assert apm.client.config.environment == CONFIG_FILE["environment"]
        assert apm.client.config.base_dir == CONFIG_FILE["base_dir"]
        assert apm.client.config.config_file == CONFIG_FILE["config_file"]

    def test_config_values_from_config_file(self):
        if not os.path.exists(STACKIFY_JSON_FILE):
            with open(STACKIFY_JSON_FILE, 'w') as json_file:
                json.dump(CONFIG_FILE, json_file)

        apm = StackifyAPM()

        assert apm.client.config.application_name == CONFIG_FILE["application_name"]
        assert apm.client.config.environment == CONFIG_FILE["environment"]
        assert apm.client.config.base_dir == CONFIG_FILE["base_dir"]
        assert apm.client.config.config_file == STACKIFY_JSON_FILE

        os.remove(STACKIFY_JSON_FILE)

    def test_basic_instrumentation(self):
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.zlib.ZLibInstrumentation",
        }

        apm = StackifyAPM(**CONFIG)
        apm.client.begin_transaction("Test for begin transaction")

        zlib.compress(b'Compressing Data')
        self.assert_span(operation='compress')

    def assert_span(self, operation):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'compression.zlib'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Compression'
        assert span_data['props']['SUBCATEGORY'] == 'Compression'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Compression'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Compression'
        assert span_data['props']['OPERATION'] == operation
