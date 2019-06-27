from mpxapi.api_base import ApiBase


class LedgerEntry(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "3.4.0"
        self.service = "Admin Storefront Service"
        self.path = "/data/LedgerEntry"