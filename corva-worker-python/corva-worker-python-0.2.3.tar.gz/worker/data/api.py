import os
import requests

from worker import exceptions


class API(object):
    HTTP_METHODS = ('get', 'post', 'patch', 'put', 'delete')
    options = {
        "api_url": "API_ROOT_URL",
        "api_key": "API_KEY",
        "app_name": "APP_NAME"
    }

    def __init__(self, *args, **kwargs):
        self.configure(self.options, kwargs)

    def configure(self, options, values):
        for attribute, environment_key in options.items():
            value = values.pop(attribute, os.getenv(environment_key, None))
            if not value:
                error = "No {0} parameter or {1} environment variable defined".format(attribute, environment_key)
                raise exceptions.Misconfigured(error)

            setattr(self, attribute, value)

    def get(self, *args, **kwargs):
        return self.call("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.call("post", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.call("patch", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.call("put", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.call("delete", *args, **kwargs)

    def call(self, method, path, **kwargs):
        content_type = kwargs.pop("content_type", "application/json")
        headers = {
            "Authorization": "API {0}".format(self.api_key),
            "Content-Type": content_type,
            "X-Corva-App": self.app_name
        }

        method = method.lower()
        if method not in self.HTTP_METHODS:
            raise exceptions.APIError("Invalid HTTP method {0}".format(method))

        http_method = getattr(requests, method)
        data = kwargs.pop("data", None)
        if not path.startswith(self.api_url):
            path = "{0}{1}".format(self.api_url, path)

        response = http_method(url=path, data=data, params=kwargs, headers=headers)

        asset_id = kwargs.get("asset_id", "Unknown") or "Unknown"

        if response.status_code == 401:
            raise exceptions.APIError("Unable to reach Corva API: {}".format(response.content))

        if response.status_code == 403:
            raise exceptions.Forbidden("No access to asset {0}".format(asset_id))

        if response.status_code == 404:
            raise exceptions.AssetNotFound("Asset {0} Not Found".format(asset_id))

        if not response.ok:
            raise exceptions.APIError("Unable to reach Corva API: {}".format(response.content))

        result = Result(response, **kwargs)
        return result


class Result(object):

    def __init__(self, response, **kwargs):
        self.response = response
        self.params = kwargs
        self.data = None

        try:
            self.data = response.json()
        except Exception:
            raise exceptions.APIError("Invalid API response")

    def __repr__(self):
        return repr(self.data)

    def __iter__(self):
        return iter(self.data)

    @property
    def status(self):
        return self.response.status_code

    @property
    def count(self):
        if not self.data:
            return 0

        if isinstance(self.data, list):
            return len(self.data)

        if isinstance(self.data, dict):
            return 1

        return 0
