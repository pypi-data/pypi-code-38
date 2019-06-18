import os


TRACEPARENT_HEADER_NAME = "stackify-apm-traceparent"
TRACE_CONTEXT_VERSION = '2.0'

KEYWORD_MAX_LENGTH = 1024

HTTP_WITH_BODY = {"POST", "PUT", "PATCH", "DELETE"}

ERROR = "error"
TRANSACTION = "transaction"
SPAN = "span"

if os.name == 'nt':
    BASE_PATH = "c:\\ProgramData\\Stackify\\Python\\"
    LOG_PATH = "{}Log\\".format(BASE_PATH)
else:
    BASE_PATH = "/usr/local/stackify/stackify-python-apm/"
    LOG_PATH = "{}log/".format(BASE_PATH)

QUEUE_TIME_INTERVAL_IN_MS = 500
QUEUE_MAX_SIZE = 1000

ASYNC_WAITING_TIME_IN_SEC = 10
ASYNC_MAX_WAITING_TIME_IN_SEC = 40

RUM_SCRIPT_SRC = "https://stckjs.azureedge.net/stckjs.js"
