import logging


class ObjectMap(object):

    def __init__(self, client, tag, resource, logger=None):
        self.log = logger if logger else logging.getLogger(__name__+'.'+resource.lower())
        self.client = client
        self.tag = tag
        self.resource = resource

    def get(self, id=None, object_number=None, height=None, width=None):
        return self.client.object.getObjectMap(id=id, number=object_number, height=height, width=width).response().result
