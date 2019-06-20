from http_server_base.tools.types import JsonSerializable, RegExpType
@property
def re_type():
    from warnings import warn
    warn("re_type is going to be deprecated. Use RegExpType instead", DeprecationWarning, 2)
    return RegExpType

from .extensions import revrange
from .extensions import server_request_to_client_request

from .config_loader import ConfigLoader
from .logging import setup_logging, logging_method, ExtendedLogger, RequestLogger, StyleAdapter
from .subrequest_classes import HttpSubrequest, HttpSubrequestResponse
from .errors import ServerError, SubrequestFailedError, SubrequestFailedErrorCodes
from .re_dict import ReDict
