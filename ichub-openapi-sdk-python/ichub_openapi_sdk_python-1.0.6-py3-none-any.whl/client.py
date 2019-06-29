from ichubOpenApi import const
from ichubOpenApi.request.requestBase import requestBase
from ichubOpenApi.request.models import Method
import json


class Client:
    def __init__(self, host=None, v='1.0.0', app_id='', sign_type='', key='', public_key='', private_key=''):
        self.request = requestBase(host=host, v=v, app_id=app_id, sign_type=sign_type, key=key, public_key=public_key,
                                   private_key=private_key)

    def uploadsupply(self, currency_id, tax_rate, items):
        """
        上传供货
        :param currency_id: U|R 币种
        :param tax_rate: 0-2 税率
        :param items: [] 供货项
        :return: bool
        """
        data = {'api_code': Method.supply, 'tax_rate': tax_rate, 'currency_id': currency_id, 'items': json.dumps(items)}
        return self.request.send_request(params=data, filter_param={'items'})
