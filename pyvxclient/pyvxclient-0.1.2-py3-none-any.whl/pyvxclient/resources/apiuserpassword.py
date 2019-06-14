import logging


class ApiUserPassword(object):

    def __init__(self, client, tag, resource, logger=None):
        self.log = logger if logger else logging.getLogger(__name__+'.'+resource.lower())
        self.client = client
        self.tag = tag
        self.resource = resource

    def get(self, username_or_email, portal_url):
        return self.client.api.getApiPassword(username_or_email=username_or_email, url=portal_url).response().result
