from .rpc import rpc
from .response import RpcResponse

from .dependency_providers import ElasticSearch

from .exceptions import ServiceException, ServiceErrorException

# Import elasticsearch
from . import elasticsearch


# Package Name
name = 'nameko_wrapper'