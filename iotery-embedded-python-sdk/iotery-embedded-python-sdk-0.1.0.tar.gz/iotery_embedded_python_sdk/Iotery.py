from requests import get, post, patch, delete
import json
from types import MethodType
import pkg_resources


def hydrate_route(path, obj):
    """Hydrates a given route path with dictionary items found in obj"""
    split_route = path.split("/")
    for s in split_route:
        if len(s) > 0 and s[0] == ":":
            path = path.replace(
                s, obj[s[1:]])
    return path


class Iotery:
    """iotery.io python library class for interacting with iotery.io platform.  Wraps the iotery.io REST API.
        Usage: 
            iotery = Iotery()
            device_type = iotery.createDeviceType(data={"name": "My Device Type", ...})

        All API specifications can be found at https://iotery.io/v1/docs/embedded
    """

    def __init__(self, base_url="https://api.iotery.io/v1"):
        self._base_url = base_url
        self._token = None
        self._headers = {
            "Content-Type": "application/json"
        }

    def set_token(self, token):
        self._token = token
        self._headers = {
            "authorization": "Bearer " + self._token, "Content-Type": "application/json"
        }


class IoteryException(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return json.dumps(self.message, indent=4, sort_keys=True)


# get the spec:
# get the spec:
resource_package = __name__
resource_path = '/api.json'
api_string = pkg_resources.resource_string(resource_package, resource_path)
_spec = json.loads(api_string)

# set up the api
for route in _spec["routes"]:

    # handle methods for each route
    if route["method"] == "GET":
        def handler(self, opts={},  __path=route["path"], **kwargs):
            hydrated_route = hydrate_route(__path, kwargs)

            res = get(self._base_url + hydrated_route, params=opts,
                        headers=self._headers)
            if res.status_code >= 400:
                raise IoteryException(res.json())

            return res.json()

    if route["method"] == "POST":
        def handler(self, opts={}, data={},  __path=route["path"], **kwargs):
            hydrated_route = hydrate_route(__path, kwargs)

            res = post(self._base_url + hydrated_route, params=opts,
                        headers=self._headers, json=data)
            if res.status_code >= 400:
                raise IoteryException(res.json())

            return res.json()

    if route["method"] == "PATCH":
        def handler(self, opts={}, data={},  __path=route["path"], **kwargs):
            hydrated_route = hydrate_route(__path, kwargs)

            res = patch(self._base_url + hydrated_route, params=opts,
                        headers=self._headers, json=data)
            if res.status_code >= 400:
                raise IoteryException(res.json())

            return res.json()

    if route["method"] == "DELETE":
        def handler(self, opts={},  __path=route["path"], **kwargs):
            hydrated_route = hydrate_route(__path, kwargs)

            res = delete(self._base_url + hydrated_route, params=opts,
                            headers=self._headers)
            if res.status_code >= 400:
                raise IoteryException(res.json())

            return res.json()
    # attach to the class
    a = setattr(Iotery, route["name"], handler)
