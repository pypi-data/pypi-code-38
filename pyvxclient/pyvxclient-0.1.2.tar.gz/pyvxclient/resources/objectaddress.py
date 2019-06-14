import logging


class ObjectAddress(object):

    def __init__(self, client, tag, resource, logger=None):
        self.log = logger if logger else logging.getLogger(__name__+'.'+resource.lower())
        self.client = client
        self.tag = tag
        self.resource = resource

    def get(self, object_number):
        return self.client.object.getObjectAddress(object_number=object_number).response().result
