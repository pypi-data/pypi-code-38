from mpxapi.api_base import ApiBase


class ProfileResult(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.3.0"
        self.service = "Workflow Data Service"
        self.path = "/data/ProfileResult"
