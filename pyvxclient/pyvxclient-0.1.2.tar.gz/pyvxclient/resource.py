from pyvxclient.decorators import paginate, handle_response
import logging


class Resource(object):
    """
      Initiate the Generic Resource Class.
    """

    _default_sort = ("id",)
    _default_limit = None

    def __init__(self, client, tag, resource, logger=None):
        self.log = logger if logger else logging.getLogger(__name__+'.'+resource.lower())
        self.client = client
        self.tag = tag
        self.resource = resource

    def __client_resource_method(self, verb):
        return getattr(getattr(self.client, self.tag), '{}{}'.format(verb, self.resource))

    @paginate
    def get(self, limit=_default_limit, sort=_default_sort, q=[], fields=[], page=None):
        client_resource_method = self.__client_resource_method('get')
        return client_resource_method(page=page, per_page=limit, sort=sort, q=q, fields=fields).response().result

    # TODO raise NotImplementedError()

    @handle_response
    def create(self, **kwargs):
        client_resource_method = self.__client_resource_method('post')
        return client_resource_method(body=kwargs).response()

    @handle_response
    def update(self, **kwargs):
        client_resource_method = self.__client_resource_method('put')
        return client_resource_method(body=kwargs).response()
