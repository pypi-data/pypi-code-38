from .util import EvolvError


class EvolvConfig:

    def __init__(self, api_domain="experiments.evolv.ai", api_key=None, bearer_token=None, api_version='v1'):
        """Holds the configuration for the Evolv Client.

        :param string api_domain: domain of the experiments API
        :param string api_key: api_key for customer's integration
        :param string bearer_token: jwt provided by auth0
        :param string api_version: api gateway usage plan id
        """
        self.__api_key = api_key
        self.__bearer_token = bearer_token
        self.__api_domain = api_domain
        self.__api_version = api_version

    @property
    def api_key(self):
        """Retrieves the configurations API key.

        :return: an api key
        :rtype: string
        """
        return self.__api_key

    @api_key.setter
    def api_key(self, api_key):
        """Sets the API key. Easily change the api key for a given config
        after its been populated.

        :param string api_key: the new api key
        """
        self.__api_key = api_key

    @property
    def bearer_token(self):
        """Retrieves the configurations bearer token.

        :return: a jwt
        :rtype: string
        """
        return self.__bearer_token

    @bearer_token.setter
    def bearer_token(self, bearer_token):
        """Sets the bearer token. Easily change the bearer token for a given config
        after its been populated.

        :param string bearer_token: the new jwt
        """
        self.__bearer_token = bearer_token

    @property
    def api_domain(self):
        """Retrieves the experiment api domain

        :return: the experiment api domain
        :rtype: string
        """
        return self.__api_domain

    @property
    def api_version(self):
        """Retrieves the version of the api to use.

        :return: api version
        :rtype: string
        """
        return self.__api_version

    class IncompleteConfiguration(EvolvError):
        """To be used when the configuration is incomplete for the desired function

        """
        pass
