from pyvxclient.decorators import paginate, handle_response
import logging


class Orders(object):
    """
      Initiate the Orders Class.
    """

    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    @paginate
    def Get(self, limit=None, sort=["id", "order_number"], q=[], fields=[], page=None):
        return self.client.order.getOrder(page=page, per_page=limit, sort=sort, q=q, fields=fields).response().result

    @handle_response(logger=logging.getLogger('pyvxclient.update.order'))
    def Create(self, **kwargs):
        return self.client.order.postOrder(body=kwargs).response()

    @handle_response(logger=logging.getLogger('pyvxclient.update.order'))
    def Update(self, **kwargs):
        return self.client.order.putOrder(body=kwargs).response()
