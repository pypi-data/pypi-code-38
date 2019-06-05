from pyvxclient.decorators import paginate
import logging


class NetworkOperator(object):
    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    @paginate
    def Get(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network_operator.getNetworkOperator(per_page=limit, sort=sort, q=q, fields=fields,
                                                               page=None).response().result

    def Create(self):
        raise NotImplementedError

    def Update(self):
        raise NotImplementedError
