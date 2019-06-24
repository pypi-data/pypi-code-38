from alas_ce0.common.client_base import EntityClientBase


class ReportClient(EntityClientBase):
    entity_endpoint_base_url = '/reporting/reports/'

    def get_content(self, id):
        return self.http_get(
            self.entity_endpoint_base_url + "{0}/_content".format(id)
        )

    def get_b2c_delivery_report(self, b2b_code, delivery_date):
        return self.http_get(
            self.entity_endpoint_base_url + "b2c-delivery/{0}/{1}".format(b2b_code, delivery_date)
        )