"""
Provides the ApiContext class
"""
__copyright__ = "Copyright 2017, Datera, Inc."


class ApiContext(object):
    """
    This object is created by the top level API object, and is passed in
    to all endpoints and entities.
    """

    def __init__(self):
        self.connection = None

        self.hostname = None
        self.username = None
        self.password = None
        self.tenant = None

        self.timeout = None
        self.secure = None
        self.version = None
        self.cert = None
        self.cert_key = None

        self._reader = None
        self.strict = True
        self.thread_local = None
        self.ldap_server = None
        self.retry_503_type = None
        self.retry_connection_type = None
        self.extra_headers = {}
        self.verify = None
        self.schema_loc = None

        self.on_entity_create_hooks = []
        self.on_entity_delete_hooks = []
        self.prepare_entity_hooks = []
        self.prepare_endpoint_hooks = []

    @property
    def reader(self):
        if not self._reader:
            self.connection.login(
                name=self.username,
                password=self.password,
                ldap_server=self.ldap_server)
            self._reader = self.connection.reader
        return self._reader

    @staticmethod
    def _call_hooks(obj, hooks):
        """ Calls a series of callbacks """
        if not hooks:
            return obj
        for hook in hooks:
            ret = hook(obj)
            if ret is not None:
                obj = ret  # hooks can modify returned object
        return obj

    def on_entity_create(self, entity):
        """ Called after an entity has been created on the system """
        return self._call_hooks(entity, self.on_entity_create_hooks)

    def on_entity_delete(self, entity):
        """ Called after an entity has been deleted from the system """
        return self._call_hooks(entity, self.on_entity_delete_hooks)

    def prepare_entity(self, entity):
        """ Called to setup an entity object returned from a REST query """
        return self._call_hooks(entity, self.prepare_entity_hooks)

    def prepare_endpoint(self, endpoint):
        """ Called to setup an endpoint object """
        return self._call_hooks(endpoint, self.prepare_endpoint_hooks)
