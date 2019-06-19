import logging
import requests
import datetime
import abc
from furl import furl
import pyark.backoff_retrier as backoff_retrier
from pyark.errors import CvaServerError, CvaClientError


class RestClient(object):

    _session = requests.Session()

    def __init__(self, url_base, endpoint_base=None, retries=5):
        self._url_base = url_base
        self._endpoint_base = endpoint_base
        self._headers = {
            'Accept': 'application/json'
        }
        self._token = None
        self._renewed_token = False
        # decorates the REST verbs with retries
        self._get = backoff_retrier.wrapper(self._get, retries)
        self._post = backoff_retrier.wrapper(self._post, retries)
        self._delete = backoff_retrier.wrapper(self._delete, retries)

    def _build_url(self, endpoint):
        f = furl(self._url_base)
        segments = []
        if self._endpoint_base:
            segments = self._endpoint_base.split("/")
        if isinstance(endpoint, (str,)):
            endpoint = endpoint.split("/")
        if isinstance(endpoint, (list,)):
            segments = segments + endpoint
        else:
            segments.append(endpoint)
        f.path.segments = segments
        return f.url

    def _set_authenticated_header(self, renew_token=False):
        if not self._token or renew_token:
            self._token = self._get_token()
        self._headers["Authorization"] = "{token}".format(token=self._token)

    @abc.abstractmethod
    def _get_token(self):
        raise ValueError("Not implemented")

    def _post(self, endpoint, payload, session=True, **params):
        if endpoint is None or payload is None:
            raise ValueError("Must define payload and endpoint before post")
        url = self._build_url(endpoint)
        if session:
            response = self._session.post(url, json=payload, params=params, headers=self._headers)
        else:
            response = requests.post(url, json=payload, params=params, headers=self._headers)
        logging.info("{method} {url}".format(
            method="POST",
            url="{}?{}".format(url, "&".join(RestClient._build_parameters(params)))
        ))
        self._verify_response(response)
        return response.json(), dict(response.headers)

    def _get(self, endpoint, session=True, **params):
        if endpoint is None:
            raise ValueError("Must define endpoint before get")
        url = self._build_url(endpoint)
        if session:
            response = self._session.get(url, params=params, headers=self._headers)
        else:
            response = requests.get(url, params=params, headers=self._headers)
        logging.info("{method} {url}".format(
            method="GET",
            url="{}?{}".format(url, "&".join(RestClient._build_parameters(params)))
        ))
        self._verify_response(response)
        return response.json(), dict(response.headers)

    def _patch(self, endpoint, session=True, **params):
        if endpoint is None:
            raise ValueError("Must define endpoint before patch")
        url = self._build_url(endpoint)
        if session:
            response = self._session.patch(url, params=params, headers=self._headers)
        else:
            response = requests.patch(url, params=params, headers=self._headers)
        logging.info("{method} {url}".format(
            method="GET",
            url="{}?{}".format(url, "&".join(RestClient._build_parameters(params)))
        ))
        self._verify_response(response)
        return response.json(), dict(response.headers)

    def _delete(self, endpoint, **params):
        if endpoint is None:
            raise ValueError("Must define endpoint before get")
        url = self._build_url(endpoint)
        response = self._session.delete(url, params=params, headers=self._headers)
        logging.info("{method} {url}".format(
            method="DELETE",
            url="{}?{}".format(url, "&".join(RestClient._build_parameters(params)))
        ))
        self._verify_response(response)
        return response.json(), dict(response.headers)

    @staticmethod
    def _build_parameters(params):
        parsed_params = []
        for k, v in params.items():
            if isinstance(v, list):
                parsed_params.extend(["{}={}".format(k, e) for e in v])
            else:
                parsed_params.append("{}={}".format(k, v))
        return parsed_params

    def _verify_response(self, response):
        logging.debug("{date} response status code {status}".format(
            date=datetime.datetime.now(),
            status=response.status_code)
        )
        if response.status_code != 200:
            logging.error(response.content)
            # first 403 renews the token, second 403 in a row fails
            if response.status_code in (403, 401) and not self._renewed_token:
                # renews the token if unauthorised
                self._set_authenticated_header(renew_token=True)
                self._renewed_token = True
                # RequestException will trigger a retry and with the renewed token it may work
                raise requests.exceptions.RequestException(response=response)
            # ValueError will not
            if 500 <= response.status_code < 600:
                raise CvaServerError("{}:{}".format(response.status_code, response.text))
            elif 400 <= response.status_code < 500:
                raise CvaClientError("{}:{}".format(response.status_code, response.text))
            else:
                raise ValueError("{}:{}".format(response.status_code, response.text))
        else:
            # once a 200 response token is not anymore just renewed, it can be renewed again if a 403 arrives
            self._renewed_token = False
