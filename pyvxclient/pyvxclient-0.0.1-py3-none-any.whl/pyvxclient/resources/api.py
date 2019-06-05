import logging


class ApiUser(object):
    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    def Get(self, limit=10, sort=["id"], q=[], fields=[]):
        return self.client.api.getApiUser(per_page=limit, sort=sort, q=q, fields=fields).response().result

    def GetPassword(self, username_or_email, portal_url):
        return self.client.api.getApiPassword(username_or_email=username_or_email, url=portal_url).response().result

    def GetSettings(self, limit=10, sort=["id"], q=[], fields=[]):
        return self.client.api.getApiUser(per_page=limit, sort=sort, q=q, fields=fields).response().result

    def GetSynchronization(self, limit=10, sort=["id"], q=[], fields=[]):
        return self.client.api.getApiSynchronization(per_page=limit, sort=sort, q=q, fields=fields).response().result

    def GetApi(self):
        return self.client.api.getApi().response().result

    def Create(self):
        raise NotImplementedError

    def Update(self):
        raise NotImplementedError

