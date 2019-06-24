from alas_ce0.common.client_base import EntityClientBase


class UserClient(EntityClientBase):
    entity_endpoint_base_url = '/management/users/'

    def authenticate(self, user_name, password):
        return self.http_post_json(self.entity_endpoint_base_url + '_authenticate',
                                   {'user_name': user_name, 'password': password})

    def reset_password(self, user_name, password):
        return self.http_post_json(self.entity_endpoint_base_url + '_reset-password',
                                   {'user_name': user_name, 'password': password})