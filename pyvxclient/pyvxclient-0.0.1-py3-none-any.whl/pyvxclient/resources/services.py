from pyvxclient.decorators import paginate
import logging


class Services(object):
    """
      Initiate the Services Class.
    """

    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    @paginate
    def Get(self, limit=None, sort=["id", "order_number"], q=[], fields=[], page=None):
        return self.client.service.getService(page=page, per_page=limit, sort=sort, q=q,
                                              fields=fields).response().result

    # @handle_response(logger=logging.getLogger('pyvxclient.create.service'))
    def Create(self, **kwargs):
        raise NotImplementedError
        # return self.client.service.postService(body=kwargs).response()

    # @handle_response(logger=logging.getLogger('pyvxclient.update.service'))
    def Update(self, **kwargs):
        raise NotImplementedError
        # return self.client.service.putService(body=kwargs).response()
