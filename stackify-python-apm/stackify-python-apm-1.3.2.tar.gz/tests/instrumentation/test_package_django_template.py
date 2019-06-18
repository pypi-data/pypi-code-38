import django
from django.conf import settings
from django.template import Context, Template
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.traces import get_transaction
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from tests.contrib.django.fixtures.testapp.settings import TEST_SETTINGS


CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class DjangoTemplateInstrumentationTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.contrib.django.apps.setup_logging')
        self.setup_logging.start()

        if not settings.configured:
            settings.configure(**TEST_SETTINGS)
            django.setup()

        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.django.template.DjangoTemplateInstrumentation",
            "stackifyapm.instrumentation.packages.django.template.DjangoTemplateSourceInstrumentation",
        }

        control.instrument()
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument()
        self.setup_logging.stop()

    def test_template(self):
        template = Template('My name is {{ name }}.')
        context = Context({'name': 'JayR'})

        result = template.render(context)

        assert result == "My name is JayR."
        self.assert_span()

    def assert_span(self):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'template.django'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Template'
        assert span_data['props']['SUBCATEGORY'] == 'Render'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Template'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Template'
