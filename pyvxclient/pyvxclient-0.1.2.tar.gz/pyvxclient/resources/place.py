import logging


class Place(object):

    def __init__(self, client, tag, resource, logger=None):
        self.log = logger if logger else logging.getLogger(__name__+'.'+resource.lower())
        self.client = client
        self.tag = tag
        self.resource = resource

    def get(self):
        return self.client.customer.getPlace().response().result
