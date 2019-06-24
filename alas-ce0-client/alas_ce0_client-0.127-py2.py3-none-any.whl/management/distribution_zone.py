from alas_ce0.common.client_base import EntityClientBase


class DistributionZoneClient(EntityClientBase):
    entity_endpoint_base_url = '/management/distribution-zones/'

    def __init__(self, country_code='cl', **kwargs):
        super(DistributionZoneClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'
