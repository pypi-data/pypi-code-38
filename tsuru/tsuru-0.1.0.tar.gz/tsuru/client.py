import os

import requests


class TsuruClient:
    _URL = os.environ.get('TSURU_URL')
    _USERNAME = os.environ.get('TSURU_USERNAME')
    _PASSWORD = os.environ.get('TSURU_PASSWORD')
    _TOKEN = None

    @classmethod
    def _get_headers(cls):
        return {
            "Authentication": cls._get_token(),
            "Content-Type": "application/json",
        }

    @classmethod
    def _get_token(cls):
        if not cls._TOKEN:
            cls._TOKEN = cls.login()
        return cls._TOKEN

    @classmethod
    def login(cls):
        login_data = f"email={cls._USERNAME}&password={cls._PASSWORD}"
        data = cls.post(resource='/auth/login', data=login_data)
        return data['token']

    @classmethod
    def get(cls, resource, pk=None, from_resource=None, from_pk=None, params=None):
        if from_resource:
            if not from_pk:
                raise UnboundLocalError()

            if pk:
                url = f'{cls._URL}/{from_resource}/{from_pk}/{resource}/{pk}'
            else:
                url = f'{cls._URL}/{from_resource}/{from_pk}/{resource}'
        elif pk:
            url = f'{cls._URL}/{resource}/{pk}'
        else:
            url = f'{cls._URL}/{resource}'

        response = requests.get(
            url=url,
            params=params,
            headers=cls._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def post(cls, resource, data):
        url = f'{cls._URL}/{resource}'

        response = requests.post(
            url=url,
            data=data,
            headers=cls._get_headers(),
        )
        response.raise_for_status()
        return response.json()
