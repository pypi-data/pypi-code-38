from ..CommonInterface import CommonInterfaceAuth
import json
import requests

class Auth(CommonInterfaceAuth):
    """
    Auth
    """
    def __init__(self, host, port=80):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}/api/v2'

    def auth(self, username, password, host=None, port=None):
        """ Authorization API

        POST method which returns an 
        authorization token to be used by other calls. 

        :param username: username for login
        :param password: password for login
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_auth = SONATAClient.Auth(HOST_URL)
                response = json.loads(sonata_auth.auth(
                                        username=USERNAME,
                                        password=PASSWORD))
        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        _endpoint = '{0}/sessions'.format(base_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = {"username": username, "password": password}

        try:
            # TODO: make verify=false as a fallback
            r = requests.post(_endpoint, headers=headers,  json=data, verify=False)
        except Exception as e:
            result["data"] = str(e)
            return result

        if r.status_code == requests.codes.ok:
            result['error'] = False

        result["data"] = r.text
        return json.dumps(result)
