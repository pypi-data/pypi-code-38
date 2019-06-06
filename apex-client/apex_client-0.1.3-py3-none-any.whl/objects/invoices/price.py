from typing import Optional

from apex_client.objects import ApexObject
from .currency import Currency


class Price(ApexObject):
    valid_properties = ['id', 'uuid', 'price', 'currency_name']
    mapped_properties = {
        'currency': 'currency_id'
    }

    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.currency_object = None

    @classmethod
    def get(cls, price_id: int) -> Optional['Price']:
        return Price._get(f'invoices/prices/{price_id}/')

    @property
    def currency(self):
        if not self.currency_object and self.currency_id:
            self.currency_object = Currency.get(self.currency_id)

        return self.currency_object

    def __str__(self):
        return f"{self.price} {self.currency_name}"
