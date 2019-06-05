from pyvxclient.decorators import paginate, handle_response
import logging


class ServiceDisruptions(object):
    """
      Initiate the ServiceDisruption Class.
    """

    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    @paginate
    def Get(self, limit=None, sort=['id'], q=[], fields=[], page=None):
        return self.client.network.getServiceDisruption(page=page, per_page=limit, sort=sort, q=q,
                                                         fields=fields).response().result

    @handle_response(logger=logging.getLogger('pyvxclient.update.service_disruption'))
    def Update(self, **kwargs):
        return self.client.network.putServiceDisruption(body=kwargs).response()
