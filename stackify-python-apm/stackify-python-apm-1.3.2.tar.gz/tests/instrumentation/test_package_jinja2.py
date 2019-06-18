from jinja2 import Template
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.traces import get_transaction

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class Jinja2InstrumentationTest(TestCase):

    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.jinja2.Jinja2Instrumentation",
        }

    def tearDown(self):
        control.uninstrument()

    def test_template_render(self):
        control.instrument()
        self.client.begin_transaction("Test for begin transaction")

        self.test = Template("Sample Template")
        self.test.render(something='World')

        self.assert_span(method='sample')

    def assert_span(self, method):

        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'template.jinja2'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Template'
        assert span_data['props']['SUBCATEGORY'] == 'Render'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Template'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Template'
