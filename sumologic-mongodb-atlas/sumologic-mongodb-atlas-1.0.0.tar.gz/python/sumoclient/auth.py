from requests.session import Session, merge_setting


class CustomSession(Session):

    def set_headers(self, header_name, header_val):
        self.headers[header_name] = header_val

    def set_auth(self, auth_obj):
        self.auth = merge_setting(self.auth, auth_obj)

    def set_params(self, token_key, token_val):
        self.params[token_key] = token_val
