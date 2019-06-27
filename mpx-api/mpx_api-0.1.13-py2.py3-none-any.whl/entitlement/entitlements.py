from mpxapi.api_base import ApiBase


class Entitlement(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.3.9"
        self.service = "Entitlement Data Service"
        self.path = "/data/Entitlement"
