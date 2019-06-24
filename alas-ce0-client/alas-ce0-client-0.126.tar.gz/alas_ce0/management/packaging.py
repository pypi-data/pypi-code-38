from alas_ce0.common.client_base import EntityClientBase


class PackagingLocationClient(EntityClientBase):
    entity_endpoint_base_url = '/management/packaging-locations/'

    def __init__(self, country_code='cl', **kwargs):
        super(PackagingLocationClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'
