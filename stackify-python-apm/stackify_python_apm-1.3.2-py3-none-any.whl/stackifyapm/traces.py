import json
import logging
import random
import threading
import uuid
from functools import wraps
from multiprocessing.managers import BaseManager

from stackifyapm import VERSION
from stackifyapm.conf import constants
from stackifyapm.conf.constants import ASYNC_WAITING_TIME_IN_SEC
from stackifyapm.conf.constants import TRACE_CONTEXT_VERSION
from stackifyapm.utils import encoding
from stackifyapm.utils import get_class_name_or_None
from stackifyapm.utils import get_method_name
from stackifyapm.utils.compat import iteritems
from stackifyapm.utils.disttracing import TraceParent
from stackifyapm.utils.helper import get_current_time_in_millis
from stackifyapm.utils.helper import is_async_span


__all__ = ("CaptureSpan", "set_transaction_name")

logger = logging.getLogger("stackifyapm.traces")
error_logger = logging.getLogger("stackifyapm.errors")

_COMPONENT_CATEGORY_MAP = {
    "database_connect": "Database",
    "database_sql": "DB Query",
    "send": "Web External",
    "cache": "Cache",
    "template": "Template",
}

_COMPONENT_DETAIL_MAP = {
    "database_connect": "Open Connection",
    "database_sql": "Execute SQL Query",
    "send": "Execute",
    "cache": "Execute",
    "template": "Template",
}

try:
    from stackifyapm.context.contextvars import get_transaction, set_transaction, get_span, set_span, clear_span  # noqa
except ImportError:
    from stackifyapm.context.threadlocal import get_transaction, set_transaction, get_span, set_span, clear_span  # noqa


class Transaction(object):
    def __init__(self, transaction_type="custom", trace_parent=None, is_sampled=True, meta_data={}):
        """
        Create a new Transaction
        """
        self.id = "{:016x}".format(random.getrandbits(64))
        self.name = None
        self.transaction_type = transaction_type
        self.context = {}
        self.start_time = get_current_time_in_millis()
        self.end_time = None
        self.is_sampled = is_sampled
        self.trace_parent = trace_parent

        self.exceptions = []
        self.spans = []

        self._has_async_spans = False
        self._thread_id = str(threading.current_thread().ident)
        self._meta_data = meta_data

    def get_id(self):
        return self.id

    def get_is_sampled(self):
        return self.is_sampled

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_context(self):
        return self.context

    def update_context(self, context):
        self.context.update(context)

    def get_has_async_spans(self):
        return self._has_async_spans

    def set_has_async_spans(self, has_async_spans):
        self._has_async_spans = has_async_spans

    def get_spans(self):
        return self.spans

    def get_trace_parent(self):
        return self.trace_parent

    def set_trace_parent(self, trace_parent):
        self.trace_parent = trace_parent

    def end_transaction(self):
        self.end_time = get_current_time_in_millis()

    def get_meta_data(self):
        return self._meta_data

    def add_exception(self, exception):
        self.exceptions.append(exception)

    def get_exceptions(self):
        return self.exceptions

    def begin_span(self, name, span_type, context=None, leaf=False, is_async=False):
        parent_span = get_span()

        if parent_span and parent_span.leaf:
            span = DroppedSpan(parent_span, leaf=True)
        else:
            span = Span(transaction=self, name=name, span_type=span_type, context=context, leaf=leaf, is_async=is_async)
            span.parent = parent_span

        if not isinstance(span, DroppedSpan):
            self.spans.append(span)

        set_span(span)
        return span

    def update_span_context(self, span_id, span_context):
        spans = [span for span in self.spans if span.id == span_id]
        if spans:
            span = spans[0]
            span.context.update(span_context)
        else:
            logger.warning("Can't find span id: {} from transaction id: {}".format(span_id, self.id))

    def end_span(self):
        span = get_span()
        if span is None:
            raise LookupError()

        if isinstance(span, DroppedSpan):
            set_span(span.parent)
            return

        span.end_time = get_current_time_in_millis()

        set_span(span.parent)
        return span

    def is_done(self):
        return all([span.end_time for span in self.spans])

    def to_dict(self):
        stacks = []
        spans = [span.to_dict() for span in self.spans]
        spans.reverse()

        # convert to key-value pair for easy access
        spans_kv = {span['id']: span for span in spans}

        # arrange span and add each child to their respective parent
        for span in spans:
            if not span['parent_id'] == span['transaction_id']:
                spans_kv[span['parent_id']]['stacks'].insert(0, spans_kv.pop(span['id']))
            else:
                stacks.insert(0, spans_kv.pop(span['id']))

        result = {
            "id": self.id,
            "call": self._get_call(),
            "reqBegin": self.start_time,
            "reqEnd": self.end_time,
            "props": self._get_props(),
            "stacks": stacks,
        }
        if self.trace_parent.span_id and self.trace_parent.span_id != self.id:
            result["parent_id"] = self.trace_parent.span_id

        if self.exceptions:
            result["exceptions"] = self.exceptions

        return json.dumps(result)

    def _get_call(self):
        call = encoding.keyword_field(self.name or "").split(" ")[-1]

        if call:
            return call

        if "request" in self.context:
            return self.context["request"]["url"]["pathname"]

        return ""

    def _get_props(self):
        service_info = self._meta_data.get('service_info')
        process_info = self._meta_data.get('process_info')
        system_info = self._meta_data.get('system_info')
        application_info = self._meta_data.get('application_info')

        base_object = {
            "CATEGORY": service_info["language"]["name"].title(),
            "THREAD_ID": self._thread_id,
            "TRACE_ID": self.trace_parent.trace_id,
            "TRACE_SOURCE": "PYTHON",
            "TRACE_TARGET": "RETRACE",
            "TRACE_VERSION": "{}".format(VERSION or TRACE_CONTEXT_VERSION or "unknown"),
            "HOST_NAME": system_info["hostname"],
            "OS_TYPE": system_info["platform"].upper(),
            "PROCESS_ID": process_info["pid"],
            "APPLICATION_PATH": "/",
            "APPLICATION_FILESYSTEM_PATH": application_info["base_dir"],
            "APPLICATION_NAME": application_info["application_name"],
            "APPLICATION_ENV": application_info["environment"],
        }

        if self.transaction_type in ['custom']:
            base_object["TRACETYPE"] = "TASK"
        else:
            base_object["TRACETYPE"] = "WEBAPP"

        if "request" in self.context:
            base_object["METHOD"] = self.context["request"]["method"]
            base_object["URL"] = self.context["request"]["url"]["full"]
            base_object["REPORTING_URL"] = self.context["request"]["url"]["pathname"]
        else:
            base_object["REPORTING_URL"] = self._get_call()

        if "response" in self.context:
            base_object["STATUS"] = self.context["response"]["status_code"]

        return base_object


class Span(object):
    __slots__ = (
        "id",
        "transaction",
        "name",
        "type",
        "context",
        "leaf",
        "parent",
        "start_time",
        "end_time",
        "is_async",
        "_thread_id",
    )

    def __init__(self, transaction, name, span_type, context=None, leaf=False, is_async=False):
        """
        Create a new Span
        """
        self.id = "{}".format(len(transaction.get_spans()) + 1)
        self.transaction = transaction
        self.name = name
        self.type = span_type
        self.context = context
        self.leaf = leaf
        self.parent = None
        self.start_time = get_current_time_in_millis()
        self.end_time = None
        self.is_async = is_async
        self._thread_id = str(threading.current_thread().ident)

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction.get_id(),
            "parent_id": self.parent.id if self.parent else self.transaction.get_id(),
            "call": encoding.keyword_field(self.type),
            "reqBegin": self.start_time,
            "reqEnd": self.end_time,
            "props": self._get_props(),
            "stacks": [],
        }

    def _get_props(self):
        base_object = {
            "CATEGORY": self._get_category(),
        }

        if self.type.split('.')[0].lower() not in ["custom"]:
            base_object["SUBCATEGORY"] = self._get_sub_catergory()

        if self.is_async:
            base_object["TRACETYPE"] = "ASYNC"
            base_object["THREAD_ID"] = self._thread_id

        if not self.context:
            return base_object

        if self.context.get("type", "").lower() not in ["cassandra", "stackify"] and self.type.split('.')[0].lower() not in ["custom"]:
            base_object["COMPONENT_CATEGORY"] = self._get_component_category()
            base_object["COMPONENT_DETAIL"] = self._get_component_detail()

        if self.context.get("type", "").lower() in ["database", "mongodb"] and "provider" in self.context:
            base_object["PROVIDER"] = self.context["provider"]

        if self.context.get("type", "").lower() in ["database", "cassandra"]:
            if "statement" in self.context:
                base_object["SQL"] = self.context["statement"]

        if self.context.get("type", "").lower() == "mongodb":
            if "collection" in self.context:
                base_object["MONGODB_COLLECTION"] = self.context["collection"]

        if "url" in self.context:
            base_object["URL"] = self.context["url"]

        if "status_code" in self.context:
            base_object["STATUS"] = self.context["status_code"]

        if "request_method" in self.context:
            base_object["METHOD"] = self.context["request_method"].upper()

        if "operation" in self.context:
            base_object["OPERATION"] = self.context["operation"]

        if "cache_key" in self.context:
            base_object["CACHEKEY"] = self.context["cache_key"]

        if "cache_name" in self.context:
            base_object["CACHENAME"] = self.context["cache_name"]

        if "row_count" in self.context:
            base_object["ROW_COUNT"] = self.context["row_count"]

        if self.context.get("template"):
            base_object["TEMPLATE"] = self.context["template"]

        if self.type.split('.')[0].lower() in ["custom"]:
            for k, v in iteritems(self.context):
                if k not in ['type', 'sub_type', 'wrapped_method', 'provider']:
                    base_object[k.upper()] = v

        # for trace/log integration
        # we will add log_id which was generated in the stackify instrumentation
        if self.context.get("log_id"):
            base_object["ID"] = self.context["log_id"]

        return base_object

    def _get_category(self):
        type = encoding.keyword_field(self.type)
        return self.context and self.context.get("type", "") or type.split('.')[0].title()

    def _get_sub_catergory(self):
        wrapped_method = self.context and self.context.get("wrapped_method")
        return wrapped_method and wrapped_method.title() or self._get_category()

    def _get_component_category(self):
        sub_type = self.context and self.context.get("sub_type", "") or ""
        return _COMPONENT_CATEGORY_MAP.get(sub_type) or self._get_category() or "Python"

    def _get_component_detail(self):
        sub_type = self.context and self.context.get("sub_type") or ""
        return _COMPONENT_DETAIL_MAP.get(sub_type) or self._get_sub_catergory() or "Other"


class DroppedSpan(object):
    __slots__ = ("leaf", "parent")

    def __init__(self, parent, leaf=False):
        self.parent = parent
        self.leaf = leaf


class TransactionManager(BaseManager):
    pass


class Tracer(object):
    def __init__(
        self,
        queue,
    ):
        """
        Create a Tracer
        """
        TransactionManager.register('Transaction', Transaction)

        self.queue = queue
        self.manager = TransactionManager()
        try:
            self.manager.start()
        except Exception as e:
            logger.debug("Error when starting manager. Details: {}".format(e))

    def begin_transaction(self, transaction_type, trace_parent=None, client=None):
        """
        Start a new transactions and bind it in a thread-local variable
        """
        meta_data = client and client.get_meta_data() or {}
        transaction = self.manager.Transaction(transaction_type, trace_parent, meta_data=meta_data)
        if trace_parent is None:
            transaction.set_trace_parent(TraceParent(
                constants.TRACE_CONTEXT_VERSION,
                str(uuid.uuid4()),
                transaction.get_id(),
            ))

        set_transaction(transaction)
        return transaction

    def end_transaction(self, transaction_name=None):
        transaction = get_transaction(clear=True)
        if transaction:
            transaction.end_transaction()
            if transaction.get_name() is None:
                transaction.set_name(transaction_name or "")

            if transaction.get_name() or 'request' in transaction.get_context() or 'response' in transaction.get_context():
                if transaction.get_has_async_spans():
                    self.queue(transaction, delay=ASYNC_WAITING_TIME_IN_SEC)
                else:
                    self.queue(transaction)
            else:
                logger.debug("Dropped transaction {}".format(transaction.get_id()))

        return transaction

    def capture_exception(self, exception=None):
        transaction = get_transaction()

        if transaction and exception:
            transaction.add_exception(exception)

        return transaction


class CaptureSpan(object):
    def __init__(self, name=None, span_type="custom", extra={}, leaf=False, is_async=False, **kwargs):
        """
        Start a new CaptureSpan
        """
        self.name = name
        self.type = span_type
        self.extra = extra
        self.leaf = leaf
        self.is_async = is_async

    def __call__(self, func):
        self.name = self.name

        @wraps(func)
        def wrapper(*args, **kwds):
            self.is_async = is_async_span()
            self.extra['type'] = 'Python'

            class_name = get_class_name_or_None(func)
            if class_name:
                self.type = '{}.{}'.format(self.type, class_name)

            self.type = '{}.{}'.format(self.type, get_method_name(func))

            with self:
                return func(*args, **kwds)

        return wrapper

    def __enter__(self):
        transaction = get_transaction()
        if transaction and transaction.get_is_sampled():
            return transaction.begin_span(self.name, self.type, context=self.extra, leaf=self.leaf, is_async=self.is_async)

    def __exit__(self, exc_type, exc_val, exc_tb):
        transaction = get_transaction()
        if transaction and transaction.get_is_sampled():
            try:
                transaction.end_span()
            except LookupError:
                error_logger.info("ended non-existing span {} of type {}".format(self.name, self.type))


def set_transaction_name(name, override=True):
    transaction = get_transaction()
    if not transaction:
        return

    if transaction.get_name() is None or override:
        transaction.set_name(name)


def set_transaction_context(data, key="custom"):
    transaction = get_transaction()
    if not transaction:
        return

    if callable(data) and transaction.get_is_sampled():
        data = data()

    transaction_context = transaction.get_context()
    if key in transaction_context:
        transaction_context[key].update(data)
    else:
        transaction_context[key] = data
    transaction.update_context(transaction_context)
