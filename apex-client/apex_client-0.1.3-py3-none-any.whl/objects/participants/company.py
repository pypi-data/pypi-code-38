from typing import Optional

from apex_client.objects import ApexObject

from .address import Address
from .network import Network


class Company(ApexObject):
    valid_properties = ['id', 'uuid', 'name', 'is_active', 'website', 'corporate_id', 'vat_number', 'default_currency',
                        'allow_invoicing', 'terms_of_payment', 'group_invoices', 'invoice_days_before_event',
                        'number_of_employees', 'city', 'default_currency_display', 'status', 'invoice_company',
                        'invoice_company_name', 'booked_events']
    date_properties = ['date_created', 'date_modified']

    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.address_ids = []
        self.address_objects = []

        self.network_ids = []
        self.network_objects = []

        if 'addresses' in json_data.keys():
            for item in json_data['addresses']:
                if isinstance(item, dict):
                    self.address_objects.append(Address(item))
                else:
                    self.address_ids.append(item)

        if 'networks' in json_data.keys():
            for item in json_data['networks']:
                if isinstance(item, dict):
                    self.network_objects.append(Network(item))
                else:
                    self.network_ids.append(item)

    @classmethod
    def get(cls, company_id: int) -> Optional['Company']:
        return Company._get(f'companies/{company_id}/')

    @property
    def addresses(self):
        if not len(self.address_objects) and len(self.address_ids):
            for address_id in self.address_ids:
                address = self.get_address(address_id)
                if address:
                    self.address_objects.append(address)

        return self.address_objects

    def get_address(self, address_id: int) -> Optional[Address]:
        return Address._get(f'companies/{self.id}/addresses/{address_id}/')

    @property
    def networks(self):
        if not len(self.network_objects) and len(self.network_ids):
            for network_id in self.network_ids:
                network = Network.get(network_id)
                if network:
                    self.network_objects.append(network)

        return self.network_objects

    def __str__(self):
        return f"{self.uuid}: {self.name}"
