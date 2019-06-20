import jwt
import requests
from requests.auth import AuthBase
import json


class TokenAuth(AuthBase):
    """Implements a custom authentication scheme."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        """Attach an API token to a custom auth header."""
        r.headers['Authorization'] = self.token
        return r


class AIH:
    def __init__(self, app_id, secret_key):
        self.__secret = 'Iz9uaoZtSV2TBO_M5m4f4Q'
        self.app_id = app_id
        self.__token = jwt.encode({'AppId': self.app_id, 'SecretKey': secret_key}, self.__secret)
        self.__url = "http://aih-api.vmod1.com"

    def recognition_faces(self, file_binary, file_name):
        try:
            path = f'{self.__url}/rekognition/faces'
            res = requests.post(path, files={'file': file_binary}, data={"filename": file_name},
                                auth=TokenAuth(self.__token))
            return res.json()
        except Exception as e:
            raise e

    def update_face_info(self, fullname, face_id):
        try:
            path = f'{self.__url}/rekognition/faces/{face_id}'
            res = requests.patch(path, data={"fullname": fullname}, auth=TokenAuth(self.__token))
            return res.json()
        except Exception as e:
            raise e

    def speak(self, text):
        try:
            path = f'{self.__url}/polly/speak'
            res = requests.post(path, data={"text": text}, auth=TokenAuth(self.__token))
            return res.json()
        except Exception as e:
            raise e
