from typing import Optional

from apex_client.objects import ApexObject


class Network(ApexObject):
    valid_properties = ['id', 'name']

    @classmethod
    def get(cls, network_id: int) -> Optional['Network']:
        return Network._get(f'networks/{network_id}/')

    def __str__(self):
        return self.name
