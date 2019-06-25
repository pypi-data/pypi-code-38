import requests
import json
from ciperror import PublisherApiRequestError


class DeliveryEfPublishRequestApi:
    """Send request"""
    def __init__(self, base_url, logger):
        self.base_url = f'{base_url}/api'
        self.logger = logger

    def _url(self, path):
        return self.base_url + path

    def send(self, body=None):
        try:
            url = self._url('/publish-request')
            self.logger.info(200, message=f'Enviando request de post Ef Delivery Service\
                API URL: {url} BODY: {json.dumps(body)}')
            if body:
                response = requests.post(url, json=body)
            else:
                response = requests.post(url)
        except Exception as ex:
            error = PublisherApiRequestError(str(ex))
            self.logger.error(error.code, error.http_status, message=error.message)
            raise error

        if response.status_code not in [200, 201, 204]:
            error = PublisherApiRequestError(response.text)
            self.logger.error(error.code, error.http_status, message=error.message)
            raise error

        return response

    def PublishRawFile(self, body):
        try:
            url = self._url('/publish-raw-file')
            self.logger.info(200, message=f'Enviando request de post Ef Delivery Service\
                 API URL: {url} BODY: {json.dumps(body)}')
            response = requests.post(url, json=body)
        except Exception as ex:
            error = PublisherApiRequestError(str(ex))
            self.logger.error(error.code, error.http_status, message=error.message)
            raise error

        if response.status_code not in [200, 201, 204]:
            error = PublisherApiRequestError(response.text)
            self.logger.error(error.code, error.http_status, message=error.message)
            raise error

        return response

    def healthcheck(self):
        url = self._url('/healthcheck')
        try:
            response = requests.get(url, timeout=2)
            if response.ok:
                return True
            error = PublisherApiRequestError(response.text)
        except Exception as ex:
            error = PublisherApiRequestError(str(ex))
            
        self.logger.error(error.code, error.http_status, message=error.message)
            
        return False
