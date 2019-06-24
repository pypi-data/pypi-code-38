from alas_ce0.common.client_base import EntityClientBase


class ServiceLevelClient(EntityClientBase):
    entity_endpoint_base_url = '/management/service-levels/'

    def __init__(self, country_code='cl', **kwargs):
        super(ServiceLevelClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'