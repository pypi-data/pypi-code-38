
import requests
import thisamericanlife.endpoints as tal_endpoints


class HttpClient(object):
    def get(self, endpoint, **kwargs):
        resp = requests.get(endpoint.format(**kwargs))
        resp.raise_for_status()
        return resp
