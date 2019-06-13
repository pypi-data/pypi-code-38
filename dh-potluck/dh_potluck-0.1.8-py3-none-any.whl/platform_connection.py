from http import HTTPStatus
from urllib.parse import urljoin

import requests
from flask import current_app


class PlatformConnectionError(Exception):
    pass


class MissingPlatformConnection(PlatformConnectionError):
    pass


class InvalidPlatformConnection(PlatformConnectionError):
    pass


class BadApiResponse(Exception):
    def __init__(self, description, response):
        message = (f'{description}\n'
                   f'HTTP Status: {response.status_code}\n'
                   f'Request URL: {response.url}\n'
                   f'Response Body: {response.text}')
        super().__init__(message)


class PlatformConnection:

    @classmethod
    def get(cls, brand_id, platform_type):
        platform_label = platform_type.capitalize()
        res = requests.get(
            urljoin(current_app.config['DH_POTLUCK_AUTH_API_URL'], '/api/platform_connections'),
            headers={'Authorization':
                     f'Application {current_app.config["DH_POTLUCK_AUTH_API_TOKEN"]}'},
            params={'platform_type': platform_type, 'brand_id': brand_id}
        )
        if not res.ok:
            raise BadApiResponse('Error making API request', res)

        try:
            platform_connection = res.json()[0]

        except IndexError:
            raise MissingPlatformConnection(f'No {platform_label} platform connection found for '
                                            f'brand {brand_id}.') from None

        if platform_connection['status'] != 'connected':
            raise InvalidPlatformConnection(f'{platform_label} platform connection for brand '
                                            f'{brand_id} is marked as '
                                            f'{platform_connection["status"]}.')

        return platform_connection

    @classmethod
    def update(cls, id, data):
        res = requests.patch(
            urljoin(current_app.config['DH_POTLUCK_AUTH_API_URL'],
                    f'/api/platform_connections/{id}'),
            headers={'Authorization':
                     f'Application {current_app.config["DH_POTLUCK_AUTH_API_TOKEN"]}'},
            json=data
        )

        if res.status_code != HTTPStatus.OK:
            raise BadApiResponse('Error making API request', res)

        return res.json()
