import re

from .client import Client

client = Client()


def get_tx_info(transaction: dict) -> dict:
    data = {
        'fecha': transaction['fecha_proceso'],
        'criterio': transaction['clave_rastreo'],
        'emisor': transaction['institucion_ordenante'],
        'receptor': transaction['institucion_beneficiaria'],
        'cuenta': transaction['cuenta_beneficiario'],
    }
    response = client.post('valida.do', data)
    if '<tr><td>' in response:
        response = re.findall('<td>(.*?)</td>', response)
        transaction_dict = dict(
            referencia=response[1],
            rastreo=response[3],
            institucion_ordenante=response[5],
            institucion_beneficiario=response[7],
            estado=response[9],
            fecha_recepcion=response[11],
            fecha_procesamiento=response[13],
        )
        return transaction_dict
    else:
        return {}
