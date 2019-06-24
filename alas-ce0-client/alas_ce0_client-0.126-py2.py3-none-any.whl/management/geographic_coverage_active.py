from alas_ce0.common.client_base import EntityClientBase


class GeographicCoverageActiveClient(EntityClientBase):
    entity_endpoint_base_url = '/management/geographic-coverages-active/'

    def __init__(self, country_code='cl', **kwargs):
        super(GeographicCoverageActiveClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'
