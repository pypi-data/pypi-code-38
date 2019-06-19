import requests
import json
from ciperror import EmailServiceRequestError


class EmailApi:
    """Send request"""

    def __init__(self, base_url, logger):
        self.base_url = f'{base_url}/api'
        self.logger = logger

    def _url(self, path):
        return self.base_url + path

    def send(self, body):
        try:
            url = self._url('/v2/email')
            self.logger.info(200, message=f'Enviando request de post o Email Service\
                API URL: {url} BODY: {json.dumps(body)}')
            response = requests.post(url, json=body)
        except Exception as ex:
            error = EmailServiceRequestError(str(ex))
            self.logger.error(error.code, error.http_status, message=error.message)
            raise error

        if response.status_code not in [200, 201, 204]:
            error = EmailServiceRequestError(response.text)
            self.logger.error(error.code, error.http_status, message=error.message)
            raise error

        return response

    def healthcheck(self):
        url = self._url('/healthcheck')
        try:
            response = requests.get(url, timeout=2)
            if response.ok:
                return True
            error = EmailServiceRequestError(response.text)
        except Exception as ex:
            error = EmailServiceRequestError(str(ex))

        self.logger.error(error.code, error.http_status, message=error.message)

        return False
