import base64

from alas_ce0.common.client_base import ApiClientBase


class ConfigurationClient(ApiClientBase):
    entity_endpoint_base_url = '/management/configurations/'

    def set(self, config_name, content):
        params = {
            'file_name': config_name,
            'base64_content': base64.encodestring(content)
        }
        return self.http_post_json(self.entity_endpoint_base_url + '_set', params)

    def get(self, config_name):
        return self.http_get(self.entity_endpoint_base_url + config_name)