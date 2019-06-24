from enum import Enum

from alas_ce0.management.task import TaskClient

from alas_ce0.common.client_base import EntityClientBase


class RouteStatusType(Enum):
    Created = 1
    Validating = 2
    Validated = 3
    InRoute = 4
    Finished = 5


class RouteSegmentStatusType(Enum):
    Created = 1
    NotValidated = 2
    Validated = 3
    Traveling = 4
    NotDelivered = 5
    Delivered = 6


class RouteClient(EntityClientBase):
    entity_endpoint_base_url = '/scheduling/routes/'

    def __init__(self, country_code='cl', **kwargs):
        super(RouteClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'

    def create_from_orders(self, params, async=True):
        if async:
            return TaskClient(**self.args).enqueue('route-create', params)
        else:
            return self.http_post_json(self.entity_endpoint_base_url + "_create-from-orders", params)

    def upload_file(self, user_name, sender_code, base64_content, file_format="txt", description=None):
        params = {
            'user_name': user_name,
            'sender_code': sender_code,
            'base64_content': base64_content,
            'format': file_format,
            'description': description,
        }
        return self.http_post_json(self.entity_endpoint_base_url + "_upload-file", params)

    def change_status_route_segment(self, id, params):
        return self.http_post_json(
            self.entity_endpoint_base_url + "{0}/_change-status-route-segment".format(id), params
        )

    def reject_route_segment(self, id, params):
        return self.http_post_json(
            self.entity_endpoint_base_url + "{0}/_reject-route-segment".format(id), params
        )

    def approve_route(self, id, params):
        return self.http_post_json(
            self.entity_endpoint_base_url + "{0}/_approve-route".format(id), params
        )

    def delete_route(self, id, params):
        return self.http_post_json(
            self.entity_endpoint_base_url + "{0}/_delete-route".format(id), params
        )

    def update_route_segments(self, id, params):
        return self.http_post_json(
            self.entity_endpoint_base_url + "{0}/_update-route-segments".format(id), params
        )

    def sync_route(self, id):
        return self.http_post_json(
            self.entity_endpoint_base_url + "{0}/_sync-route".format(id), {}
        )
