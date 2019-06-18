from boto3.session import Session
from botocore.awsrequest import AWSResponse
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.traces import get_transaction
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class BotocoreInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.botocore.BotocoreInstrumentation",
        }

    def setUpSuccess(self):
        self.parsed_response = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        self.continueSetup()

    def setUpFailed(self):
        self.parsed_response = {'ResponseMetadata': {'HTTPStatusCode': 400}}
        self.continueSetup()

    def continueSetup(self):
        self.http_response = AWSResponse(None, 200, {}, None)
        self.make_request_patch = mock.patch('botocore.endpoint.Endpoint.make_request')
        self.make_request_mock = self.make_request_patch.start()
        self.make_request_mock.return_value = (self.http_response, self.parsed_response)
        self.session = Session(aws_access_key_id="foo", aws_secret_access_key="bar", region_name="us-west-2")

        control.instrument()
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        self.make_request_patch.stop()
        control.uninstrument()

    def test_successful_request(self):
        self.setUpSuccess()

        ec2 = self.session.client("ec2")
        ec2.describe_instances()

        self.assert_span(status=200)

    def test_unsuccessful_request(self):
        self.setUpFailed()

        ec2 = self.session.client("ec2")
        ec2.describe_instances()

        self.assert_span(status=400)

    def assert_span(self, status=None):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'ext.http.aws'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Http'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Web External'
        assert span_data['props']['URL'] == 'https://ec2.us-west-2.amazonaws.com'
        assert span_data['props']['STATUS'] == status
        assert span_data['props']['OPERATION'] == 'DescribeInstances'
