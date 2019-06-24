from alas_ce0.common.client_base import EntityClientBase


class B2CClient(EntityClientBase):
    entity_endpoint_base_url = '/delivery/b2cs/'

    def __init__(self, country_code='cl', **kwargs):
        super(B2CClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'
