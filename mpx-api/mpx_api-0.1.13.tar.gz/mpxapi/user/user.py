from mpxapi.api_base import ApiBase


class User(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)
        self.schema = "1.5.0"
        self.service = "User Data Service"
        self.path = "/data/User"
