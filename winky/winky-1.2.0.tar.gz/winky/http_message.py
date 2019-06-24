import requests


class HTTPMessage:

    def __init__(self, body=""):
        self.__body = body
        self.__headers = {}
        self.__code = 200

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, text):
        self.__body = text

    @property
    def code(self):
        return self.__code

    @code.setter
    def code(self, code):
        self.__code = code

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, headers):
        self.__headers = headers

    def set_body_from_file(self, path):
        with open(path, 'r') as file:
            self.__body = file.read()

    def post(self, url, port, metod="/", timeout=10):
        endpoint = f"{url}:{port}{metod}"
        response = requests.post(endpoint,
                                 headers=self.__headers,
                                 data=self.__body.encode(),
                                 timeout=timeout,
                                 verify=False)
        return self.__make_response_message(response)

    def get(self, url, port, metod="/", timeout=10):
        endpoint = f"{url}:{port}{metod}"
        response = requests.get(endpoint,
                                headers=self.__headers,
                                timeout=timeout,
                                verify=False)
        return self.__make_response_message(response)

    @staticmethod
    def __make_response_message(response):
        response_message = HTTPMessage(response.text)
        response_message.headers = response.headers
        response_message.__code = response.status_code
        return response_message
