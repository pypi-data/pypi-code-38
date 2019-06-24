from alas_ce0.common.client_base import EntityClientBase


class B2BClient(EntityClientBase):
    entity_endpoint_base_url = '/management/b2bs/'

    def __init__(self, country_code='cl', **kwargs):
        super(B2BClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'

    def get_billing_rate_content(self, id):
        return self.http_get(
            self.entity_endpoint_base_url + "{0}/_billing-rate-content".format(id)
        )


class IntermediateCarrierClient(EntityClientBase):
    entity_endpoint_base_url = '/management/intermediate-carriers/'

    def __init__(self, country_code='cl', **kwargs):
        super(IntermediateCarrierClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'


class RegionalPartnerClient(EntityClientBase):
    entity_endpoint_base_url = '/management/regional-partners/'

    def __init__(self, country_code='cl', **kwargs):
        super(RegionalPartnerClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'