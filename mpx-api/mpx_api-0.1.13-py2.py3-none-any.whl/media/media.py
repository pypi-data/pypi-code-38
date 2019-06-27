from mpxapi.api_base import ApiBase


class Media(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.9.0"
        self.searchSchema = "1.0.0"
        self.service = "Media Data Service"
        self.path = "/data/Media"
