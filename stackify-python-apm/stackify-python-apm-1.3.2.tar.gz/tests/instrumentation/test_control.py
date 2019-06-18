from unittest import TestCase
try:
    from unittest.mock import patch
except Exception:
    from mock import patch

from stackifyapm.instrumentation.control import instrument
from stackifyapm.instrumentation.control import uninstrument


class InstrumentObject(object):
    instrumented = False

    def instrument(self, client=None):
        self.instrumented = True

    def uninstrument(self, client=None):
        self.instrumented = False


def generate_empty_generator():
    return []


def generate_one_instrumentation_object():
    return [InstrumentObject()]


class InstrumentTest(TestCase):

    @patch('stackifyapm.instrumentation.register.get_instrumentation_objects')
    def test_should_not_raise_error_on_empty_instrumentation(self, mock_instrumentation_objects):
        mock_instrumentation_objects.return_value = generate_empty_generator()

        instrument()

    @patch('stackifyapm.instrumentation.register.get_instrumentation_objects')
    def test_should_instrument_object(self, mock_instrumentation_objects):
        instrumentations = generate_one_instrumentation_object()
        mock_instrumentation_objects.return_value = instrumentations

        instrument()

        assert instrumentations
        for instrumentation in instrumentations:
            assert instrumentation.instrumented


class UninstrumentTest(TestCase):

    @patch('stackifyapm.instrumentation.register.get_instrumentation_objects')
    def test_should_not_raise_error_on_empty_uninstrumentation(self, mock_instrumentation_objects):
        mock_instrumentation_objects.return_value = generate_empty_generator()

        uninstrument()

    @patch('stackifyapm.instrumentation.register.get_instrumentation_objects')
    def test_should_instrument_object(self, mock_instrumentation_objects):
        instrumentations = generate_one_instrumentation_object()
        mock_instrumentation_objects.return_value = instrumentations

        instrument()
        assert instrumentations
        for instrumentation in instrumentations:
            assert instrumentation.instrumented

        uninstrument()
        assert instrumentations
        for instrumentation in instrumentations:
            assert instrumentation.instrumented is False
