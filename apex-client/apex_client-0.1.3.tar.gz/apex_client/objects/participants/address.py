from apex_client.objects import ApexObject


class Address(ApexObject):
    valid_properties = ['id', 'uuid', 'type', 'position', 'extra_address_field', 'address_row_1', 'address_row_2',
                        'address_row_3', 'address_row_4', 'zip_code', 'city', 'state', 'country']
    date_properties = ['date_created', 'date_modified']

    def __str__(self):
        return f"{self.address_row_1 if self.address_row_1 else ''} {self.city}"
