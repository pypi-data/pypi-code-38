from mpxapi.api_base import ApiBase


class RuleSet(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)
        self.schema = "2.6.0"
        self.service = "Commerce Configuration Data Service"
        self.path = "/data/RuleSet"
