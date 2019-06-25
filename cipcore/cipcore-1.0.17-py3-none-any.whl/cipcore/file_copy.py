import requests
from ciperror import FileCopyApiRequestError


class FileCopyApi:

    def __init__(self, base_url, logger):
        self.base_url = base_url + '/api'
        self.logger = logger

    def _url(self, path):
        return self.base_url + path

    def copy_file(self, body):
        url = self._url('/filecopy')
        return self.request_maker(body, url)

    def move_file(self, body):
        url = self._url('/movefile')
        return  self.request_maker(body, url)

    def request_maker(self, body, url):
        try:
            self.logger.info(200, message="Chamando o File Copy Service - BODY: {}"
                             .format(body))
            response = requests.post(url, json=body, timeout=None)

            if response.status_code not in [200, 201, 204]:
                error = FileCopyApiRequestError(response.text)
                self.logger.error(error.code, error.http_status, message=error.message)
                raise error

            return response
        except Exception as ex:
            error = FileCopyApiRequestError(str(ex) + ' URL: {}'.format(url))
            self.logger.error(code=error.code, status=error.http_status, message=error.message)
            raise error

    def healthcheck(self):
        url = self._url('/healthcheck')
        try:
            response = requests.get(url, timeout=2)
            if response.ok:
                return True
            error = FileCopyApiRequestError(response.text)
            self.logger.error(error.code, error.http_status, message=error.message)

        except Exception as ex:
            error = FileCopyApiRequestError(str(ex))
            self.logger.error(error.code, error.http_status, message=error.message)

        return False