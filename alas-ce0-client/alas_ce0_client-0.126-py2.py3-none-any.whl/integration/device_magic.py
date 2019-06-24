from alas_ce0.common.client_base import ApiClientBase


class DeviceMagicClient(ApiClientBase):
    entity_endpoint_base_url = '/integration/devicemagic/'

    def get_devices(self):
        return self.http_get_json(self.entity_endpoint_base_url + 'devices')

    def get_pending_dispatches(self):
        return self.http_get_json(self.entity_endpoint_base_url + 'pending-dispatches')

    def revoke_form(self, device_id, form_id):
        return self.http_post_json(self.entity_endpoint_base_url + 'revoke-form', {
            'device_id': device_id,
            'form_id': form_id
        })