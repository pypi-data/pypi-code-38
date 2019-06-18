from stackifyapm.contrib.django.context_processors import rum_tracing
from stackifyapm.base import Client
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.conf.constants import RUM_SCRIPT_SRC


CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class DangoRumTracingTest(TestCase):

    def test_rum_tracing_no_transaction(self):

        rum_data = rum_tracing('request')

        assert rum_data == {}

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_with_transaction(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = rum_tracing('request')

        assert rum_data
        assert rum_data['stackifyapm_inject_rum']

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

        assert rum_data['stackifyapm_inject_rum'] == expected_return
