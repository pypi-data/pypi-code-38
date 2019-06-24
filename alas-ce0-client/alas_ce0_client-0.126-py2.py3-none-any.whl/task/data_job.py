from alas_ce0.common.client_base import EntityClientBase


class DataJobClient(EntityClientBase):
    entity_endpoint_base_url = '/task/data-jobs/'

    def get_content(self, id):
        return self.http_get(
            self.entity_endpoint_base_url + "{0}/_content".format(id)
        )