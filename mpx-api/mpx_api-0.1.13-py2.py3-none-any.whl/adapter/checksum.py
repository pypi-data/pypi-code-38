from mpxapi.api_base import ApiBase


class Checksum(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.2.0"
        self.service = "Ingest Data Service"
        self.path = "/data/Checksum"
