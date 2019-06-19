import os
from typing import Optional

import requests


class Client:
    def __init__(self, jsessionid: Optional[str] = None):
        jsessionid = jsessionid or os.environ['STP_JSESSIONID']
        self.base_url = 'https://prod.stpmex.com/spei/'
        self.session = requests.Session()
        self.session.cookies.set('JSESSIONID', jsessionid)
        self.session.headers['User-Agent'] = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        )
        self.interface = 2
        self.base_data = {
            'btnBuscar': 1,
            'id1f_hf_0': '',
            'topologia': '',
            'importeDrop': 0,
            'rfcCEPField': '',
            'tipoPagoDrop': '',
            'importeField': '',
            'contraparteDrop': '',
            'consultaXFechaDrop': 0,
            'claveRastreoField': '',
            'rfcOrdenanteField': '',
            'timestamp:tiempoDrop': 0,
            'nombreOrdenanteField': '',
            'insOperanteDrop': '90646',
            'cuentaOrdenanteField': '',
            'rfcBeneficiarioField': '',
            'nombreBeneficiaroField': '',
            'cuentaBeneficiarioField': '',
            'timestampDev:tiempoDropDev': 0,
        }

    def get(self, url: str, **kwargs) -> str:
        return self.request('get', url, {}, **kwargs)

    def post(self, url: str, data: dict, **kwargs) -> str:
        data = {**self.base_data, **data}
        return self.request('post', url, data, **kwargs)

    def request(
        self,
        method: str,
        url: str,
        data: dict,
        increment_interface: bool = True,
        **kwargs
    ) -> str:
        url = self.base_url + url
        response = self.session.request(method, url, data=data, **kwargs)
        if increment_interface:
            self.interface += 1
        return response.text
