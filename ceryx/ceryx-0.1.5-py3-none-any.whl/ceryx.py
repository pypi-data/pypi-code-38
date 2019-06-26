from requests import Response, Session


class CeryxClient:
    def __init__(self, base_url: str):
        self.session = Session()
        self.base_url = base_url
        self.api_root = f"{self.base_url}/api"

    def _get_route_url(self, host):
        return f"{self.api_root}/routes/{host}/"

    def _get_payload_from_kwargs(
        self, host, target, enforce_https, mode, certificate_path, key_path
    ):
        payload = {
            "source": host,
            "target": target,
            "settings": {
                "enforce_https": enforce_https,
                "mode": mode,
                "certificate_path": certificate_path,
                "key_path": key_path,
            },
        }
        return payload

    def _request(self, method, url, payload={}):
        kwargs = {} if method == "get" else {"json": payload}
        response: Response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def list_routes(self):
        return self._request("get", f"{self.api_root}/routes/").json()

    def get_route(self, host: str):
        route_url = self._get_route_url(host)
        return self._request("get", route_url).json()

    def delete_route(self, host: str):
        route_url = self._get_route_url(host)
        self._request("delete", route_url)
        return None

    def create_route(
        self,
        host,
        target,
        enforce_https=False,
        mode="proxy",
        certificate_path=None,
        key_path=None,
    ):
        payload = self._get_payload_from_kwargs(
            host=host,
            target=target,
            enforce_https=False,
            mode="proxy",
            certificate_path=None,
            key_path=None,
        )
        response = self._request("post", f"{self.api_root}/routes/", payload)
        return response.json()

    def update_route(
        self,
        host,
        target,
        enforce_https=False,
        mode="proxy",
        certificate_path=None,
        key_path=None,
    ):
        payload = self._get_payload_from_kwargs(
            host=host,
            target=target,
            enforce_https=False,
            mode="proxy",
            certificate_path=None,
            key_path=None,
        )
        route_url = self._get_route_url(host)
        return self._request("put", route_url, payload).json()
