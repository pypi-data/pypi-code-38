from alas_ce0.common.client_base import EntityClientBase


class CrossDockingLocationClient(EntityClientBase):
    entity_endpoint_base_url = '/management/cross-docking-locations/'

    def __init__(self, country_code='cl', **kwargs):
        super(CrossDockingLocationClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'
