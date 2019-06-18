import json
import os
from unittest import TestCase

try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.traces import get_transaction
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control

from tests.instrumentation.fixtures.module_test import CustomClassOne
from tests.instrumentation.fixtures.module_test import CustomClassTwo
from tests.instrumentation.fixtures.module_test import CustomClassThree
from tests.instrumentation.fixtures.module_test import CustomClassFour
from tests.instrumentation.fixtures.module_test import CustomClassFive
from tests.instrumentation.fixtures.module_test import CustomClassSix
from tests.instrumentation.fixtures.module_test import CustomClassSeven
from tests.instrumentation.fixtures.module_test import CustomClassEight


STACKIFY_JSON_FILE = 'stackify.json'

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "CONFIG_FILE": STACKIFY_JSON_FILE,
}

INSTRUMENTATION = {
    "instrumentation": [{
        "class": "CustomClassOne",
        "method": "custom_method_one",
        "module": "tests.instrumentation.fixtures.module_test"
    }, {
        "class": "CustomClassTwo",
        "method": "custom_method_two",
        "module": "tests.instrumentation.fixtures.module_test",
        "trackedFunction": False
    }, {
        "class": "CustomClassThree",
        "method": "custom_method_three",
        "module": "tests.instrumentation.fixtures.module_test",
        "trackedFunction": True
    }, {
        "class": "CustomClassFour",
        "method": "custom_method_four",
        "module": "tests.instrumentation.fixtures.module_test",
        "trackedFunction": True,
        "trackedFunctionName": "{ClassName}#{MethodName}"
    }, {
        "class": "CustomClassFive",
        "method": "custom_method_five",
        "module": "tests.instrumentation.fixtures.module_test",
        "trackedFunction": True,
        "trackedFunctionName": "Tracked Function {ClassName}#{MethodName}",
        "extra": {
            "custom_key": "custom value"
        }
    }, {
        "class": "CustomClassSix",
        "method": "custom_method_six",
        "module": "tests.instrumentation.fixtures.module_test",
        "transaction": True
    }, {
        "class": "CustomClassSeven",
        "method": "custom_method_seven",
        "module": "tests.instrumentation.fixtures.module_test",
        "transaction": True
    }, {
        "class": "CustomClassEight",
        "method": "custom_method_eight",
        "module": "tests.instrumentation.fixtures.module_test",
        "transaction": True
    }]
}


class CustomInstrumentationTest(TestCase):
    def setUp(self):
        if not os.path.exists(STACKIFY_JSON_FILE):
            with open(STACKIFY_JSON_FILE, 'w') as json_file:
                json.dump(INSTRUMENTATION, json_file)

        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.custom.CustomInstrumentation",
        }
        control.instrument(client=self.client)
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument(client=self.client)
        get_transaction(clear=True)
        os.remove(STACKIFY_JSON_FILE)

    def test_basic_custom_instrumentation(self):
        CustomClassOne().custom_method_one()

        self.assert_span(call='custom.CustomClassOne.custom_method_one')

    def test_custom_instrumentation_with_tracked_function_false(self):
        CustomClassTwo().custom_method_two()

        self.assert_span(call='custom.CustomClassTwo.custom_method_two')

    def test_custom_instrumentation_with_tracked_function_true(self):
        CustomClassThree().custom_method_three()

        self.assert_span(
            call='custom.CustomClassThree.custom_method_three',
            tracked_func='CustomClassThree.custom_method_three',
        )

    def test_custom_instrumentation_with_tracked_function_and_name(self):
        CustomClassFour().custom_method_four()

        self.assert_span(
            call='custom.CustomClassFour.custom_method_four',
            tracked_func='CustomClassFour#custom_method_four',
        )

    def test_custom_instrumentation_with_tracked_function_and_name_and_extra(self):
        CustomClassFive().custom_method_five()

        self.assert_span(
            call='custom.CustomClassFive.custom_method_five',
            tracked_func='Tracked Function CustomClassFive#custom_method_five',
            extra=True
        )

    def assert_span(self, call=None, tracked_func=None, extra=None):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == call
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Python'
        if tracked_func:
            assert span_data['props']['TRACKED_FUNC'] == tracked_func

        if extra:
            assert span_data['props']['CUSTOM_KEY'] == "custom value"


class CustomTransactionInstrumentationTest(TestCase):
    def setUp(self):
        if not os.path.exists(STACKIFY_JSON_FILE):
            with open(STACKIFY_JSON_FILE, 'w') as json_file:
                json.dump(INSTRUMENTATION, json_file)

        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.custom.CustomInstrumentation",
        }

        # making sure we clear transaction
        get_transaction(clear=True)

    def tearDown(self):
        control.uninstrument(client=self.client)
        os.remove(STACKIFY_JSON_FILE)

    @mock.patch("stackifyapm.base.Client.transaction_handler")
    def test_custom_transaction_instrumentation(self, transaction_handler_mock):
        control.instrument(client=self.client)

        CustomClassSix().custom_method_six()

        assert transaction_handler_mock.called
        self.assert_transaction(
            transaction=transaction_handler_mock.call_args_list[0][0][0],
            call="custom.CustomClassSix.custom_method_six",
            stacks_count=0,
        )

    @mock.patch("stackifyapm.base.Client.transaction_handler")
    def test_custom_transaction_instrumentation_with_custom_span(self, transaction_handler_mock):
        control.instrument(client=self.client)

        CustomClassSeven().custom_method_seven()

        assert transaction_handler_mock.called

        self.assert_transaction(
            transaction=transaction_handler_mock.call_args_list[0][0][0],
            call="custom.CustomClassSeven.custom_method_seven",
            stacks_count=1,
        )
        self.assert_span_from_transaction(
            transaction=transaction_handler_mock.call_args_list[0][0][0],
            call='custom.CustomClassOne.custom_method_one'
        )

    @mock.patch("stackifyapm.base.Client.transaction_handler")
    def test_custom_transaction_instrumentation_with_exception(self, transaction_handler_mock):
        control.instrument(client=self.client)

        with self.assertRaises(Exception):
            CustomClassEight().custom_method_eight()

        assert transaction_handler_mock.called

        self.assert_transaction(
            transaction=transaction_handler_mock.call_args_list[0][0][0],
            call="custom.CustomClassEight.custom_method_eight",
            stacks_count=0,
            exception=True
        )

    def test_custom_transaction_instrumentation_but_transaction_already_exists(self):
        control.instrument(client=self.client)
        self.client.begin_transaction("transaction_test")

        CustomClassSix().custom_method_six()

        self.assert_span(call='custom.CustomClassSix.custom_method_six')

    def assert_transaction(self, transaction, call=None, stacks_count=0, exception=False):
        assert transaction

        transaction_data = json.loads(transaction.to_dict())

        assert transaction_data["id"]
        assert transaction_data["call"] == call
        assert transaction_data["reqBegin"]
        assert transaction_data["reqEnd"]
        assert transaction_data["props"]
        assert transaction_data["props"]["TRACETYPE"] == "TASK"
        assert transaction_data["props"]["APPLICATION_NAME"] == CONFIG["APPLICATION_NAME"]
        assert transaction_data["props"]["APPLICATION_ENV"] == CONFIG["ENVIRONMENT"]
        assert transaction_data["props"]["REPORTING_URL"] == call
        assert len(transaction_data["stacks"]) == stacks_count
        assert not transaction_data["props"].get("URL")
        assert not transaction_data["props"].get("METHOD")
        assert not transaction_data["props"].get("STATUS")

        if exception:
            assert transaction_data["exceptions"]
            assert transaction_data["exceptions"][0]["Frames"]
            assert transaction_data["exceptions"][0]["Timestamp"]
            assert transaction_data["exceptions"][0]["Exception"] == "Exception"
            assert transaction_data["exceptions"][0]["CaughtBy"] == "CustomClassEight"
            assert transaction_data["exceptions"][0]["Message"] == "Some exception"

    def assert_span(self, call=None):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        self.assert_span_data(span_data=span_data, call=call)

    def assert_span_from_transaction(self, transaction, call):
        assert transaction

        transaction_data = json.loads(transaction.to_dict())
        span_data = transaction_data['stacks'][0]

        self.assert_span_data(span_data=span_data, call=call)

    def assert_span_data(self, span_data, call):
        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == call
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Python'
