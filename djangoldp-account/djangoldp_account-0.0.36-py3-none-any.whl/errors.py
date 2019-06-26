class LDPLoginError(Exception):
    _errors = {
        'invalid_request': "The request provider parameter must contains an url or an email",
        'invalid_state': "Invalid state",
        'wrong_issuer': "Cannot find OP client from this issuer",
        'cannot_get_provider_info': "Cannot get provider informations",
        'cannot_get_webid': "Cannot get the webid",
        'cannot_confirm_webid': "Cannot confirm the webid. Is your authentication server host same as your webid host ?",
        'cannot_register': "Unable to register, is the provider accepting registration ? If not contact <todo : give an email> to make a manual registration"
    }

    def __init__(self, error=None, dict=None):
        if dict is None:
            self.error = error
            self.description = self._errors.get(error)
        else:
            self.error = dict['error']
            self.description = dict['error_description']

    def create_dict(self):
        dic = {
            'error': self.error,
            'error_description': self.description,
        }

        return dic


class WebFingerError(Exception):
    _errors = {
        'invalid_request': "The request provider parameter must contains an url or an email",
        'invalid_acct_format': "Invalid acct format"
    }

    def __init__(self, error=None, dict=None):
        if dict is None:
            self.error = error
            self.description = self._errors.get(error)
        else:
            self.error = dict['error']
            self.description = dict['error_description']

    def create_dict(self):
        dic = {
            'error': self.error,
            'error_description': self.description,
        }

        return dic