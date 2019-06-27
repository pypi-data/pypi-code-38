from mpxapi.api_base import ApiBase


class FeedConfig(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "2.2.0"
        self.service = "Feeds Data Service"
        self.path = "/data/FeedConfig"

    def apply_schema(self, params):
        params.update({"schema": self.schema})
        return params
