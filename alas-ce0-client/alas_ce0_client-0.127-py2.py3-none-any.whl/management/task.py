from alas_ce0.common.client_base import ApiClientBase


class TaskClient(ApiClientBase):
    entity_endpoint_base_url = '/management/tasks/'

    def enqueue(self, queue_name=None, params=None):
        if params is None:
            params = dict()

        if not queue_name:
            queue_name = 'default'

        return self.http_post_json(self.entity_endpoint_base_url + queue_name, params)