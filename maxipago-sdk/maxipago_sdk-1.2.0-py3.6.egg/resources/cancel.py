# coding: utf-8
from io import BytesIO
from maxipago.utils import etree
from maxipago.resources.base import Resource
from maxipago.exceptions import PaymentException


class CancelResource(Resource):

    def process(self):
    
        tree = etree.parse(BytesIO(self.data))
        error_code = tree.find('errorCode')
        if error_code is not None and error_code.text != '0':
            error_message = tree.find('errorMsg').text
            raise PaymentException(message=error_message)

        fields = [
            ('errorCode', 'processor_code'),
            ('errorMessage', 'error_message'),
            ('command', 'acao'),
            ('time', 'transaction_timestamp'),
            ('result', 'processor_message')
        ]

        for f_name, f_translated in fields:
            field = tree.find(f_name)
            if field is not None:
                setattr(self, f_translated, field.text)
