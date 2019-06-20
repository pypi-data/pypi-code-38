import requests
from rambler_kassa.exceptions import RamblerKassaException


class Request:
    @staticmethod
    def get(url):
        response = requests.get(url)
        try:
            data = response.json()
        except Exception as error:
            raise RamblerKassaException(error.args)
        if data.get('Code'):
            raise RamblerKassaException(data.get('Message'))
        return data
