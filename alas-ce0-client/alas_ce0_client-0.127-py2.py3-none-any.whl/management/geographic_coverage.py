from alas_ce0.common.client_base import EntityClientBase


class GeographicCoverageClient(EntityClientBase):
    entity_endpoint_base_url = '/management/geographic-coverages/'

    def __init__(self, country_code='cl', **kwargs):
        super(GeographicCoverageClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'
