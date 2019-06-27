from mpxapi.api_base import ApiBase


class PublishProfile(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.9.0"
        self.service = "Publish Data Service"
        self.path = "/data/PublishProfile"
