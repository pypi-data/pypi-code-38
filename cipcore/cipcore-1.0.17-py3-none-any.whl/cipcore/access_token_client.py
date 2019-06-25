import requests
from ciperror import ClientCredentialsTokenError
import base64


class TokenApi:

    def __init__(self, logger, client_id, secret):
        self.logger = logger
        self.client_id = client_id
        self.secret = secret
        self.url = "https://accounts.backstage.globoi.com/token"

    def request_token(self):
        try:
            self.logger.info(200, message="Chamando o Accounts Backstage para criar credencias do cliente")
            auth_basic = self.encode()
            headers = {'Authorization': "Basic {}".format(auth_basic),
                       'Content-Type': "application/x-www-form-urlencoded",
                       'cache-control': "no-cache"
                       }
            payload = "grant_type=client_credentials&undefined="
            response = requests.post(self.url, data=payload, headers=headers, timeout=5)
            if response.status_code is not 200:
                error = ClientCredentialsTokenError(response.text)
                self.logger.error(error.code, error.http_status, message=error.message)
                raise error

            access_token = response.json()['access_token']
            return access_token
        except Exception as ex:
            error = ClientCredentialsTokenError(str(ex))
            self.logger.error(code=error.code, status=error.http_status, message=error.message)
            raise error

    def encode(self):
        credentials = f'{self.client_id}:{self.secret}'
        str_to_b = str.encode(credentials)
        encoded = base64.b64encode(str_to_b)
        return encoded.decode()