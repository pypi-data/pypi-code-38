from alas_ce0.common.client_base import ApiClientBase


class WhatsappClient(ApiClientBase):
    entity_endpoint_base_url = '/integration/whatsapp/'

    def receive_message(self, params):
        return self.http_post_json(self.entity_endpoint_base_url + '_receive-message', params)