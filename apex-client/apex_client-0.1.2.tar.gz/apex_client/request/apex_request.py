import functools
import logging
import urllib.parse
from typing import Optional

from django.conf import settings

from apex_auth.apex_request import ApexRequest as AuthRequest
from requests import Response, get, patch

LOGGER = logging.getLogger(__name__)


def return_json(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs) -> dict:
        response = f(self, *args, **kwargs)

        if response.status_code >= 299:
            if response.status_code >= 500:
                LOGGER.error(f"Error received from Apex server: {response.status_code} Server error")
                return {
                    'status_code': response.status_code,
                    'response': {
                        'error': 'Server error'
                    }
                }
            else:
                LOGGER.error(f"Error received from Apex server: {response.status_code}: {response.json()}")

        return {
            'status_code': response.status_code,
            'response': response.json()
        }

    return wrapper


class ApexRequest:
    base_url = f"{settings.APEX_SERVER}api/v1/"

    @staticmethod
    def _get_headers(data=None):
        headers = AuthRequest.create_request_headers(settings.APEX_PUBLIC_KEY, settings.APEX_PRIVATE_KEY, data)

        headers.update({
            "Content-type": "application/json"
        })

        return headers

    @staticmethod
    @return_json
    def get(path: str, params: Optional[dict] = None) -> Response:
        LOGGER.info(f'GET: {path}, params: {params}')
        path = urllib.parse.urljoin(ApexRequest.base_url, path, allow_fragments=True)

        return get(path, params, headers=ApexRequest._get_headers())

    @staticmethod
    @return_json
    def patch(path: str, value: dict) -> Response:
        LOGGER.info(f'PATCH: {path}, value: {value}')
        path = urllib.parse.urljoin(ApexRequest.base_url, path, allow_fragments=True)

        return patch(path, value, headers=ApexRequest._get_headers(value))

    @staticmethod
    def search(path: str, params: dict) -> dict:
        LOGGER.info(f'search: {path}, params: {params}')

        if 'limit' not in params:
            params.update({'limit': 25})

        if 'page' not in params:
            params.update({'page': 0})

        return ApexRequest.get(path, params)

    @staticmethod
    def search_all(path: str, params: Optional[dict] = None) -> Optional[list]:
        LOGGER.info(f'search all: {path}, params: {params}')
        done = False
        results = []

        if not params:
            params = {
                'limit': 25,
                'page': 0
            }
        else:
            params.update({
                'limit': 25,
                'page': 0
            })

        while not done:
            response = ApexRequest.search(path, params)

            if response['status_code'] == 200:
                if response['response']['next'] is None:
                    done = True
                else:
                    params['page'] += 1

                results.extend(response['response']['results'])
            else:
                return None

        return results
