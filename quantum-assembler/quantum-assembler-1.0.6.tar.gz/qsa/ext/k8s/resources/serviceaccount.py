from .base import Resource
from .prefixable import Prefixable
from .persistable import Persistable


class ServiceAccount(Resource, Prefixable, Persistable):
    api_version = 'v1'
    kind = 'ServiceAccount'
    group = 'accounts'
    stage = 'iam'
