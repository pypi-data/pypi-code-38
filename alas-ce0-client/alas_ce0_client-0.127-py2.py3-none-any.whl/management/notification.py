from enum import Enum

from alas_ce0.common.client_base import ApiClientBase


class NotificationMessageType(Enum):
    Success = 1
    Warning = 2
    Failed = 3
    System = 4
    Processing = 5


class NotificationClient(ApiClientBase):
    entity_endpoint_base_url = '/management/notifications/'

    def notify_user(self, resource_name, params=None):
        if params is None:
            params = dict()

        return self.http_post_json(self.entity_endpoint_base_url + 'user/' + resource_name, params)

    def notify_message(self, params):
        return self.http_post_json(self.entity_endpoint_base_url + 'message', params)

    def notify_slack(self, params):
        return self.http_post_json(self.entity_endpoint_base_url + 'slack', params)