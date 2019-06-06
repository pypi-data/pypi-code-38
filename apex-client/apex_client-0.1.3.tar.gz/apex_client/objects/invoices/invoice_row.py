from apex_client.objects import ApexObject

from .price import Price


class InvoiceRow(ApexObject):
    valid_properties = ['id', 'uuid', 'economy_account_1', 'economy_account_2', 'description', 'discount']
    mapped_properties = {
        'invoice': 'invoice_id'
    }

    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.price_object = None
        self.price_id = None

        self.invoice_object = None
        self.invoice_id = None

        if 'price' in json_data.keys():
            if isinstance(json_data['price'], dict):
                self.price_object = Price(json_data['price'])
            else:
                self.price_id = json_data['price']

    @classmethod
    def get(cls, invoice_id, invoice_row_id):
        return InvoiceRow._get(f'invoices/{invoice_id}/rows/{invoice_row_id}/')

    @property
    def price(self):
        if not self.price_object and self.price_id:
            self.price_object = Price.get(self.price_id)

        return self.price_object

    @property
    def invoice(self):
        from .invoice import Invoice

        if not self.invoice_object and self.invoice_id:
            self.invoice_object = Invoice.get(self.invoice_id)

        return self.invoice_object

    def __str__(self):
        return f"{self.id}: {self.description}"
