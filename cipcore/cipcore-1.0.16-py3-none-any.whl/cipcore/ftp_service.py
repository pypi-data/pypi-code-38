import requests
from ciperror import NotificationError, FTPServiceRequestError
from urllib.parse import urlparse
import os


class FTPService(object):

    def __init__(self, base_url, sftp_uri, logger, callback_url):
        self.base_url = f'{base_url}/api'
        self.logger = logger
        self.sftp_uri = sftp_uri
        self.callback_url = callback_url

    def _url(self, path):
        return self.base_url + path

    def send_file(self, delivery_job, destination_root=None):

        url = self._url('/upload-file')

        try:
            json_body = self.create_json_body(delivery_job, destination_root)
            self.logger.info(200, message="Chamando o FTP Service para fazer o upload do job: {}: URL: {} BODY: {}"
                             .format(str(delivery_job), url, json_body))

            response = requests.post(url, json=json_body)
            if response.status_code not in [200, 201, 204]:
                error = FTPServiceRequestError(response.text)
                self.logger.error(error.code, error.http_status, message=error.message)
                raise error
            
            return response

        except KeyError as ex:
            ex = NotificationError(
                "ftp-service", "Erro ao chamar o ftp-service: " + str(ex))
            self.logger.error(code=ex.code, status=ex.http_status, message=ex.message)
            return False
        except Exception as ex:
            ex = NotificationError(
                "ftp-service", "Erro ao chamar o ftp-service: " + str(ex))
            self.logger.error(code=ex.code, status=ex.http_status, message=ex.message)
            return False

    def create_json_body(self, delivery_job, destination_root=None):

        parsed_sftp_url = urlparse(self.sftp_uri)
        files_to_upload = []
        for file in delivery_job['files']:
            if destination_root is not None:
                out = destination_root + os.path.basename(file['path'])
            else:
                out = os.path.basename(file['path'])
            files_to_upload.append({
                "in": file['path'],
                "out": out,
                "status": ""
            })
        delivery_job.pop('files', None)

        json_body = {
            "callback": self.callback_url,
            "body": {
                "host": parsed_sftp_url.hostname,
                "port": parsed_sftp_url.port,
                "user": parsed_sftp_url.username,
                "password": parsed_sftp_url.password,
                "files_to_upload": files_to_upload
            }
        }
        json_body['body'].update(delivery_job)

        return json_body

    def healthcheck(self):
        url = self._url('/healthcheck')
        try:
            response = requests.get(url, timeout=2)
            if response.ok:
                return True
            error = FTPServiceRequestError(response.text)
        except Exception as ex:
            error = FTPServiceRequestError(str(ex))

        self.logger.error(error.code, error.http_status, message=error.message)

        return False

