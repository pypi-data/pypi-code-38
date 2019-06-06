from apex_client.objects import ApexObject


class Currency(ApexObject):
    valid_properties = ['id', 'uuid', 'name', 'short_name']

    @classmethod
    def get(cls, currency_id: int):
        return Currency._get(f'invoices/currencies/{currency_id}/')

    def __str__(self):
        return self.name
