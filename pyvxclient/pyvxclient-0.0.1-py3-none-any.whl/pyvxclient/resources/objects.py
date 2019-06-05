import logging
from pyvxclient.decorators import paginate, handle_response


class Objects(object):
    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    @paginate
    def Get(self, ip_address=None, limit=10, sort=["id"], q=[], fields=[], page=None):
        req = self.client.object.getObject(per_page=limit, sort=sort, ip_address=ip_address, q=q, fields=fields,
                                           page=page)
        self.log.debug(req.future.request.url)
        response = req.response()
        result = response.result
        return result

    @handle_response(logger=logging.getLogger('pyvxclient.create.object'))
    def Create(self, **kwargs):
        return self.client.object.postObject(body=kwargs).response()

    @handle_response(logger=logging.getLogger('pyvxclient.update.object'))
    def Update(self, **kwargs):
        return self.client.object.putObject(body=kwargs).response()

    def GetAddress(self, object_number):
        data = self.client.object.getObjectAddress(object_number=object_number).response().result
        return

    def GetInfo(self, object_number):
        data = self.client.object.getObjectInfo(number=object_number).response().result
        return

    def GetMap(self, id=None, object_number=None, height=None, width=None):
        data = self.client.object.getObjectMap(id=id, number=object_number, height=height, width=width)
        return data
