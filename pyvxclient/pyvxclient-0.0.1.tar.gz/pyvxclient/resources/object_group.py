from pyvxclient.decorators import paginate
import logging


class ObjectGroup(object):
    """
      created (string, optional),
      description (string, optional),
      id (string, optional),
      name (string, optional),
      updated (string, optional)

    """

    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    @paginate
    def Get(self, limit=10, sort=["id"], q=[], fields=[], page=None):
        return self.client.network_operator.getObjectGroup(per_page=limit, sort=sort, q=q, fields=fields,
                                                           page=page).response().result

    def Create(self):
        raise NotImplementedError

    def Update(self):
        raise NotImplementedError
