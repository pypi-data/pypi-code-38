from mpxapi.api_base import ApiBase


class Key(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.2.1"
        self.service = "Key Data Service"
        self.path = "/data/Key"
