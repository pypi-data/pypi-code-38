import base64

import ecdsa


class ApiKey(object):

    def __init__(self, api_key):
        # type: (ecdsa.SigningKey) -> None
        self._api_key = api_key

    def get_key_seed_str(self):
        # type: () -> str
        return base64.b64encode(self._api_key.to_string())

    def __str__(self):
        # type: () -> str
        return str(self.get_key_seed_str())


class UserAccessApi(object):

    def __init__(self, user_name, policy_id, key):
        # type: (str, str, ecdsa.SigningKey) -> None
        self._user_name = user_name
        self._policy_id = policy_id
        self._api_key = ApiKey(key)

    @property
    def user_name(self):
        return self._user_name

    @property
    def policy_id(self):
        return self._policy_id

    @property
    def api_key(self):
        return self._api_key.get_key_seed_str()

    def __repr__(self):
        return 'UserAccessApiKey({},{},{})'.format(self.user_name,
                                                   self.policy_id,
                                                   self.api_key)

    def __str__(self):
        return "User Name: {}\nPolicy Id: {}\nAPI Key: {}\n".format(self.user_name,
                                                                    self.policy_id,
                                                                    self.api_key)
