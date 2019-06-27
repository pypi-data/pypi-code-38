import requests


class Client:
    def __init__(self):
        self.base_url = 'http://www.banxico.org.mx/cep/'
        self.session = requests.Session()
        self.session.headers['User-Agent'] = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        )
        self.base_data = {
            'tipoCriterio': 'T',
            'receptorParticipante': 0,
            'monto': '',
            'captcha': '',
            'tipoConsulta': 0,
        }

    def post(self, url: str, data: dict, **kwargs) -> str:
        data = {**self.base_data, **data}
        return self.request('post', url, data, **kwargs)

    def request(self, method: str, url: str, data: dict, **kwargs) -> str:
        url = self.base_url + url
        response = self.session.request(method, url, data=data, **kwargs)
        return response.text
