__all__ = ("VERSION")

name = "stackify-python-apm"

try:
    VERSION = __import__("pkg_resources").get_distribution("stackifyapm").version
except Exception:
    VERSION = None

from stackifyapm.base import Client  # noqa
from stackifyapm.conf import setup_logging  # noqa
from stackifyapm.instrumentation.control import instrument  # noqa
from stackifyapm.instrumentation.control import uninstrument  # noqa
from stackifyapm.traces import CaptureSpan  # noqa
from stackifyapm.traces import set_transaction_context  # noqa
from stackifyapm.traces import set_transaction_name  # noqa
