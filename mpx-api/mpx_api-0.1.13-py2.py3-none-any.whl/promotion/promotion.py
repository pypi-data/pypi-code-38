from mpxapi.api_base import ApiBase


class Promotion(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "3.1.0"
        self.service = "Promotion Data Service"
        self.path = "/data/Promotion"
