import json
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import Span
from stackifyapm.traces import Tracer
from stackifyapm.traces import Transaction
from stackifyapm.traces import clear_span
from stackifyapm.traces import get_span
from stackifyapm.traces import get_transaction
from stackifyapm.traces import set_transaction
from stackifyapm.traces import set_transaction_name
from stackifyapm.traces import set_transaction_context
from stackifyapm.utils.disttracing import TraceParent

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class TransactionTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.tracer = self.client.tracer

    def tearDown(self):
        clear_span()

    def test_transaction_creation(self):
        transaction = Transaction("request", None, meta_data=self.client.get_meta_data())

        assert transaction
        assert transaction.id
        assert transaction.start_time
        assert not transaction.end_time
        assert transaction.context == {}
        assert transaction.spans == []
        assert transaction.exceptions == []

    def test_begin_span(self):
        transaction = Transaction("request", None, meta_data=self.client.get_meta_data())
        span = transaction.begin_span('test_span', 'test_span_type', context={}, leaf=False)

        assert span
        assert span.name == 'test_span'
        assert span.start_time
        assert not span.end_time
        assert span == get_span()

    def test_end_span(self):
        transaction = Transaction("request", None, meta_data=self.client.get_meta_data())
        transaction.begin_span('test_span', 'test_span_type', context={}, leaf=False)
        span = transaction.end_span()

        assert span
        assert span.name == 'test_span'
        assert span.start_time
        assert span.end_time
        assert not get_span()

    def test_end_span_with_no_span(self):
        transaction = Transaction("request", None, meta_data=self.client.get_meta_data())
        with self.assertRaises(LookupError):
            transaction.end_span()

    def test_add_exception(self):
        transaction = Transaction("request", None, meta_data=self.client.get_meta_data())
        transaction.add_exception('some exception')

        assert transaction.exceptions[0] == 'some exception'

    def test_to_dict(self):
        context = {
            "wrapped_method": "Execute",
            "provider": "postgres",
            "type": "Database",
            "sub_type": "database_sql",
            "statement": "Select * from sample",
        }
        trace_parent = TraceParent("2.0", "some_id", None)

        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.begin_span("postgres", "database", context=context, leaf=False)
        transaction.add_exception('some exception')
        transaction.end_span()
        transaction_dict = json.loads(transaction.to_dict())

        assert transaction_dict["props"]
        assert transaction_dict["props"]["CATEGORY"] == "Python"
        assert transaction_dict["props"]["APPLICATION_FILESYSTEM_PATH"] == "path/to/application/"
        assert transaction_dict["props"]["APPLICATION_NAME"] == "sample_application"
        assert transaction_dict["props"]["APPLICATION_ENV"] == "production"
        assert transaction_dict["exceptions"] == ['some exception']
        assert len(transaction_dict["stacks"]) == 1

    def test_to_dict_with_request_context(self):
        trace_parent = TraceParent("2.0", "some_id", None)

        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.context = {
            "request": {
                "url": {
                    "pathname": "/somepath",
                    "full": "host.com/some_id",
                },
                "method": "get"
            }
        }
        transaction_dict = json.loads(transaction.to_dict())

        assert transaction_dict["props"]
        assert transaction_dict["props"]["METHOD"] == "get"
        assert transaction_dict["props"]["REPORTING_URL"] == "/somepath"
        assert transaction_dict["props"]["URL"] == "host.com/some_id"

    def test_to_dict_with_response_context(self):
        trace_parent = TraceParent("2.0", "some_id", None)

        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.context = {
            "response": {
                "status_code": 200,
            }
        }
        transaction_dict = json.loads(transaction.to_dict())

        assert transaction_dict["props"]
        assert transaction_dict["props"]["STATUS"] == 200

    def test_multiple_span(self):
        trace_parent = TraceParent("2.0", "some_id", None)

        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.begin_span('test_span', 'test_span_type', context={}, leaf=False)
        transaction.end_span()
        transaction.begin_span('test_span', 'test_span_type', context={}, leaf=False)
        transaction.end_span()

        transaction_dict = json.loads(transaction.to_dict())

        assert len(transaction_dict['stacks']) == 2

    def test_tree_span(self):
        trace_parent = TraceParent("2.0", "some_id", None)

        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.begin_span('test_span', 'test_span_type_1', context={}, leaf=False)
        transaction.begin_span('test_span', 'test_span_type_2', context={}, leaf=False)
        transaction.end_span()
        transaction.end_span()

        transaction_dict = json.loads(transaction.to_dict())

        assert len(transaction_dict['stacks']) == 1
        assert transaction_dict['stacks'][0]['call'] == 'test_span_type_1'
        assert len(transaction_dict['stacks'][0]['stacks']) == 1
        assert transaction_dict['stacks'][0]['stacks'][0]['call'] == 'test_span_type_2'


class SpanTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.tracer = self.client.tracer
        self.trace_parent = TraceParent("2.0", "some_id", None)
        self.transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())

    def tearDown(self):
        clear_span()

    def test_span_creation(self):
        span = Span(self.transaction, 'span_test', 'span_test_type', context={}, leaf=False)
        assert span
        assert span.id
        assert span.start_time
        assert not span.end_time
        assert span.name == 'span_test'
        assert span.type == 'span_test_type'

    def test_to_dict(self):
        context = {
            "wrapped_method": "Execute",
            "provider": "our_db",
            "type": "Database",
            "sub_type": "database_sql",
            "statement": "Select * from sample",
            "row_count": 1,
        }
        span = Span(self.transaction, 'db.sample_database', 'database', context=context, leaf=False)
        span_dict = span.to_dict()

        assert span_dict['id']
        assert span_dict['transaction_id'] == self.transaction.id
        assert span_dict['call'] == 'database'
        assert span_dict['reqBegin']
        assert span_dict['props']
        assert span_dict['props']['CATEGORY'] == "Database"
        assert span_dict['props']['SUBCATEGORY'] == "Execute"
        assert span_dict['props']['COMPONENT_CATEGORY'] == "DB Query"
        assert span_dict['props']['COMPONENT_DETAIL'] == "Execute SQL Query"
        assert span_dict['props']['PROVIDER'] == "our_db"
        assert span_dict['props']['SQL'] == "Select * from sample"
        assert span_dict['props']['ROW_COUNT'] == 1

    def test_to_dict_with_no_context(self):
        span = Span(self.transaction, 'db.sample_database', 'others', context={}, leaf=False)
        span_dict = span.to_dict()

        assert span_dict['id']
        assert span_dict['transaction_id'] == self.transaction.id
        assert span_dict['call'] == 'others'
        assert span_dict['reqBegin']
        assert span_dict['props']
        assert span_dict['props']['CATEGORY'] == "Others"
        assert span_dict['props']['SUBCATEGORY'] == "Others"


class DroppedSpanTest(TestCase):
    def test_dropped_span_creation(self):
        dropped_span = DroppedSpan('parent')

        assert dropped_span.parent == 'parent'


class TracerTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)

    def tearDown(self):
        get_transaction(clear=True)

    def test_trace_creation(self):
        tracer = Tracer(self.client.queue_listener.enqueue)
        assert tracer

    def test_begin_transaction(self):
        tracer = Tracer(self.client.queue_listener.enqueue)
        transaction = tracer.begin_transaction('request', None, self.client)
        assert transaction
        assert transaction == get_transaction()

    def test_capture_exception(self):
        tracer = Tracer(self.client.queue_listener.enqueue)
        transaction = tracer.begin_transaction('request', None, self.client)
        tracer.capture_exception('some exception')
        assert transaction
        assert transaction.get_exceptions() == ['some exception']


@CaptureSpan()
def decorated_function():
    pass


@CaptureSpan(extra={'some_custom_key': 'some value'})
def decorated_function_with_extra():
    pass


class CaptureSpanTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.tracer = Tracer(self.client.queue_listener.enqueue)

    def tearDown(self):
        clear_span()
        get_transaction(clear=True)

    def test_capture_span_creation(self):
        self.tracer.begin_transaction('request', None, self.client)
        with CaptureSpan(name='span_test', span_type="span_test_type", extra={'provider': 'stackify_test'}, leaf=False):
            pass

        transaction = get_transaction()

        assert transaction
        assert len(transaction.get_spans()) == 1
        assert transaction.get_spans()[0].name == 'span_test'

    def test_decorator_span(self):
        self.tracer.begin_transaction('request', None, self.client)

        decorated_function()

        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'custom.decorated_function'
        assert span_data['props']['CATEGORY'] == 'Python'

    def test_decorator_span_with_extra(self):
        self.tracer.begin_transaction('request', None, self.client)

        decorated_function_with_extra()

        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'custom.decorated_function_with_extra'
        assert span_data['props']['CATEGORY'] == 'Python'
        assert span_data['props']['SOME_CUSTOM_KEY'] == 'some value'


class SetTransactionUtilsTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.tracer = self.client.tracer
        self.transaction = Transaction("request", None, meta_data=self.client.get_meta_data())
        set_transaction(self.transaction)

    def tearDown(self):
        get_transaction(clear=True)

    def test_set_transaction_name(self):
        set_transaction_name('some_name')

        assert self.transaction.name == 'some_name'

    def test_set_transaction_context(self):
        set_transaction_context('some_context', "response")

        assert self.transaction.context['response'] == 'some_context'
