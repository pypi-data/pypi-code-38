import traceback

from msrest.exceptions import ClientRequestError
from requests.exceptions import ConnectionError


def retry_if_connection_error(exception):
    """Return True if we should retry (in this case when it's an IOError), False otherwise
    :param exception:
    """
    return isinstance(exception, ClientRequestError) or \
           isinstance(exception, ConnectionError) or \
           is_pool_closed_error(exception)


def is_pool_closed_error(exception):
    execption_message_list = traceback.format_exception_only(type(exception), exception)
    execption_message = "".join(execption_message_list)
    return "pool is closed" in execption_message.lower()


def retry_if_result_none(result):
    """Return True if we should retry (in this case when result is None), False otherwise"""
    return result is None


def retry_if_result_none_or_empty(result):
    """Return True if we should retry (in this case when result is None or empty), False otherwise"""
    return not result
