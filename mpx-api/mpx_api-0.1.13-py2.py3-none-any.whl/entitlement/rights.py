from mpxapi.api_base import ApiBase


class Rights(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.3.7"
        self.service = "Entitlement Data Service"
        self.path = "/data/Rights"
