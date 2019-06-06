from typing import Optional

from apex_client.objects import ApexObject


class Type(ApexObject):
    valid_properties = ['id', 'uuid', 'name', 'number_of_events']
    date_properties = ['date_created', 'date_modified']

    @classmethod
    def get(cls, type_id: int) -> Optional['Type']:
        return Type._get(f"events/types/{type_id}/")

    def __str__(self):
        return f"{self.name}"
