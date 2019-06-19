from urllib.parse import urljoin

import time
import requests

from django.conf import settings


class ApiError(BaseException):
    pass


class GlossaryService(object):

    register_url = urljoin(settings.GLOSSARY_SERVICE_URL, "/register-app")
    json_model_url = urljoin(settings.GLOSSARY_SERVICE_URL, "/get-json-models")

    @classmethod
    def request_log(cls, status_code):
        if status_code != 200:
            raise ApiError(
                "Ошибка при регистрации приложения. Код - {}"
                .format(status_code)
            )

    @classmethod
    def register(cls, update_url):
        r = requests.post(cls.register_url, {"update_url": update_url})
        cls.request_log(r.status_code)
        return r.json()["token"]

    @classmethod
    def get_json_models(cls):
        r = requests.get(cls.json_model_url)
        cls.request_log(r.status_code)
        return r.json()
