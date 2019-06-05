from pyvxclient.decorators import paginate, handle_response
import logging


class Customers(object):
    """
      Initiate the Customers Class.
    """

    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    @paginate
    def Get(self, limit=None, sort=["id", "order_number"], q=[], fields=[], page=None):
        return self.client.customer.getCustomer(page=page, per_page=limit, sort=sort, q=q,
                                                fields=fields).response().result

    @handle_response(logger=logging.getLogger('pyvxclient.create.customer'))
    def Create(self, **kwargs):
        return self.client.customer.postCustomer(body=kwargs).response()

    @handle_response(logger=logging.getLogger('pyvxclient.update.customer'))
    def Update(self, **kwargs):
        return self.client.customer.putCustomer(body=kwargs).response()
