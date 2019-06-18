from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule


CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class SampleInstrumentation(AbstractInstrumentedModule):
    name = "test_instrument"
    instrument_list = [("unittest", "TestCase")]


class SampleInstrumentation2(AbstractInstrumentedModule):
    name = "test_instrument"
    instrument_list = [("unittest", "TestCase")]
    called = False

    def call(self, module, method, wrapped, instance, args, kwargs):
        self.called = True


class AbstractInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)

    def test_abstract_instrumentation_creation(self):
        instrument = SampleInstrumentation()

        assert instrument.name == "test_instrument"

    def test_should_return_instrumented_list(self):
        instrument = SampleInstrumentation()

        assert instrument.get_instrument_list() == [("unittest", "TestCase")]

    def test_should_not_instrumented_by_default(self):
        instrument = SampleInstrumentation()

        assert instrument.instrumented is False

    def test_should_have_get_wrapped_name_method(self):
        instrument = SampleInstrumentation()

        assert hasattr(instrument, 'get_wrapped_name')

    def test_should_have_call_method(self):
        instrument = SampleInstrumentation()

        assert hasattr(instrument, 'call')

    def test_should_have_call_if_sampling(self):
        instrument = SampleInstrumentation()

        assert hasattr(instrument, 'call')

    def test_should_raise_error_if_not_implemented(self):
        instrument = SampleInstrumentation()

        with self.assertRaises(NotImplementedError) as context:
            instrument.call(None, None, None, None, None, None)

        assert context.exception.__class__.__name__ == 'NotImplementedError'

    def test_should_not_raise_error_if_implemented(self):
        instrument = SampleInstrumentation2()
        instrument.call(None, None, None, None, None, None)

        assert instrument.called

    def test_instrument(self):
        instrument = SampleInstrumentation2()
        instrument.instrument()

        assert instrument.instrumented

    def test_uninstrument(self):
        instrument = SampleInstrumentation2()
        instrument.instrument()
        assert instrument.instrumented

        instrument.uninstrument()
        assert instrument.instrumented is False
