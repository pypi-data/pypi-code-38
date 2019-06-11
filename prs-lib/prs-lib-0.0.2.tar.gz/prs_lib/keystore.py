from .request import request
from .sign_utility import hash_by_password

__all__ = ['Keystore', ]


class Keystore:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def get_by_email(self, email, password):
        """
        :param email: str
        :param password: str
        """
        data = {
            'email': email,
            'passwordHash': hash_by_password(email, password),
        }
        return request(
            self.config.host,
            method='POST',
            path='/keystore/login/email',
            data=data,
            headers={'Content-Type': 'application/json'},
            debug=self.config.debug,
        )

    def get_by_phone(self, phone, code):
        """
        :param phone: str
        :param code: str
        """
        data = {
            'phone': phone,
            'code': code,
        }
        return request(
            self.config.host,
            method='POST',
            path='/keystore/login/phone',
            data=data,
            headers={'Accept': 'application/json'},
            debug=self.config.debug,
        )
