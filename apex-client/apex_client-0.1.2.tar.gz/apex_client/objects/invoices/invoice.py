from typing import Optional

from apex_client.objects import ApexObject
from apex_client.objects.events import Event
from apex_client.objects.participants import Company, Participant
from apex_client.request import ApexRequest
from .currency import Currency
from .price import Price


class Invoice(ApexObject):
    valid_properties = ['id', 'uuid', 'event_name', 'company_name', 'participant_name', 'status', 'status_display',
                        'payment_type', 'currency_id', 'currency_shortname', 'our_reference', 'our_reference_name',
                        'our_reference_email', 'attention', 'attention_email', 'reference', 'event_economy_account_1',
                        'event_acconomy_account_2', 'financial_id', 'total_cost', 'total_cost_default_currency']
    date_properties = ['date', ]
    mapped_properties = {
        'company': 'company_id',
        'event': 'event_id',
        'participant': 'participant_id'
    }

    def __init__(self, json_data: dict):
        from .invoice_row import InvoiceRow

        super().__init__(json_data)

        self.company_object = None
        self.currency_object = None
        self.event_object = None
        self.invoice_row_objects = []
        self.participant_object = None

        if 'invoice_rows' in json_data.keys():
            for item in json_data['invoice_rows']:
                if isinstance(item, dict):
                    self.invoice_row_objects.append(InvoiceRow(item))

        if 'total_price' in json_data.keys():
            self.total_price = Price(json_data['total_price'])
        else:
            self.total_price = Price({})

        if 'total_price_default_currency' in json_data.keys():
            self.total_price_default_currency = Price(json_data['total_price_default_currency'])
        else:
            self.total_price_default_currency = Price({})

    @classmethod
    def get(cls, invoice_id: int) -> Optional['Invoice']:
        return Invoice._get(f'invoices/{invoice_id}/')

    @property
    def company(self) -> Optional['Company']:
        if not self.company_object and self.company_id:
            self.company_object = Company.get(self.company_id)

        return self.company_object

    @property
    def event(self) -> Optional['Event']:
        if not self.event_object and self.event_id:
            self.event_object = Event.get(self.event_id)

        return self.event_object

    @property
    def participant(self) -> Optional['Participant']:
        if not self.participant_object and self.participant_id:
            self.participant_object = Participant.get(self.participant_id)

        return self.participant_object

    @property
    def invoice_rows(self) -> list:
        from .invoice_row import InvoiceRow

        if not self.invoice_row_objects:
            results = ApexRequest.search_all(f'invoices/{self.id}/rows/')

            if results:
                for item in results:
                    self.invoice_row_objects.append(InvoiceRow(item))

        return self.invoice_row_objects

    @property
    def currency(self) -> Optional['Currency']:
        if not self.currency_object and self.currency_id:
            self.currency_object = Currency.get(self.currency_id)

        return self.currency_object

    def __str__(self):
        return f"{self.event_name}: {self.participant_name}"
