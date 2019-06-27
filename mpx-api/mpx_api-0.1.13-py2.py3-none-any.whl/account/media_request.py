from mpxapi.api_base import ApiBase


class MediaRequest(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.3.7"
        self.service = "Account Data Service"
        self.path = "/data/MediaRequest"
