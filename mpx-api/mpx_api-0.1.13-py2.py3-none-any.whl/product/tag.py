from mpxapi.api_base import ApiBase


class ProductTag(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "2.6.0"
        self.service = "Product Data Service"
        self.path = "/data/ProductTag"
