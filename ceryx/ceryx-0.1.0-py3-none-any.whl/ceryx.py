from requests import Response, Session


class CeryxClient(Session):
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _get_route_url(self, host):
        return f"{self.base_url}/{host}/"

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
        response: Response = self.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def list_routes(self):
        return self._request("get", self.base_url)

    def get_route(self, host: str):
        route_url = self._get_route_url(host)
        return self._request("get", route_url)

    def delete_route(self, host: str):
        route_url = self._get_route_url(host)
        return self._request("delete", route_url)

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
        return self._request("post", self.base_url, payload)

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
        return self._request("put", route_url, payload)
