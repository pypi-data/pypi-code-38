from unittest import TestCase

from stackifyapm.instrumentation import register
from stackifyapm.instrumentation.register import register as reg
from stackifyapm.instrumentation.register import get_instrumentation_objects


class RegisterTest(TestCase):

    def setUp(self):
        register._cls_registers = set()

    def test_register_should_be_added(self):
        reg('some_string')

        assert register._cls_registers == {'some_string'}

    def test_register_should_not_add_empty_string(self):
        reg('')

        assert register._cls_registers == set()

    def test_register_should_not_add_blank_space_string(self):
        reg(' ')

        assert register._cls_registers == set()


class GetInstrumentationObjectTest(TestCase):

    def test_should_return_instrumented_object(self):
        register._cls_registers = {
            "tests.instrumentation.fixtures.instrumentation_test.TestInstrumentation",
        }

        instrumentation_objects = get_instrumentation_objects()

        assert instrumentation_objects

        for instrumentation_object in instrumentation_objects:
            assert instrumentation_object.name == 'test_instrumentation'
