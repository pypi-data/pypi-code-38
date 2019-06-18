from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.conf.constants import RUM_SCRIPT_SRC
from stackifyapm.traces import get_transaction
from stackifyapm.utils.helper import get_current_time_in_millis
from stackifyapm.utils.helper import get_current_time_in_string
from stackifyapm.utils.helper import get_rum_script_or_None


CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class TestGetCurrentTimeInMillis(TestCase):

    def test_should_be_float(self):
        time = get_current_time_in_millis()

        assert isinstance(time, float)

    def test_should_contain_at_least_13_characters(self):
        time = str(get_current_time_in_millis())

        assert len(time) >= 13

    def test_should_contain_decemal_point(self):
        time = str(get_current_time_in_millis())

        assert time.count('.') == 1


class TestGetCurrentTimeInString(TestCase):

    def test_should_be_string(self):
        time = get_current_time_in_string()

        assert isinstance(time, str)

    def test_should_be_13_characters(self):
        time = get_current_time_in_string()

        assert len(time) == 13

    def test_should_not_contain_decemal_point(self):
        time = get_current_time_in_string()

        assert time.count('.') == 0


class TestRumTracing(TestCase):
    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_no_value(self, get_property_info_mock):
        get_property_info_mock.return_value = {}
        self.client = Client(CONFIG)

        transaction = get_transaction()
        self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = get_rum_script_or_None(transaction)

        assert rum_data is None

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_has_only_device_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID"}
        self.client = Client(CONFIG)

        transaction = get_transaction()
        self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = get_rum_script_or_None(transaction)

        assert rum_data is None

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_has_only_device_id_and_clinet_rum_domain(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = get_transaction()
        self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = get_rum_script_or_None(transaction)

        assert rum_data is None

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_has_only_client_id_and_client_rum_domain(self, get_property_info_mock):
        get_property_info_mock.return_value = {"clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = get_transaction()
        self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = get_rum_script_or_None(transaction)

        assert rum_data is None

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_with_transaction(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = get_transaction()
        transaction = self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = get_rum_script_or_None(transaction)

        assert rum_data

        expected_return = '<script src="{}" data-host="{}" data-requestId="V2|{}|{}|{}" data-a="{}" data-e="{}" data-enableInternalLogging="{}" async> </script>'.format(
            RUM_SCRIPT_SRC,
            "Client Rum Domain",
            transaction.get_trace_parent().trace_id,
            "Client ID",
            "Device ID",
            CONFIG["APPLICATION_NAME"],
            CONFIG["ENVIRONMENT"],
            False,
        )

        assert rum_data == expected_return
