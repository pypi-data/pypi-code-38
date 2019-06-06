from typing import Optional

from apex_client.objects import ApexObject
from .event import Event


class Area(ApexObject):
    valid_properties = ['id', 'uuid', 'name', 'slug', 'number_of_events', 'number_of_templates']
    date_properties = ['date_created', 'date_modified']

    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.area_templates = []
        self.area_events = []

        if 'area_templates' in json_data.keys():
            for item in json_data['area_templates']:
                self.area_templates.append(Event(item))

        if 'area_events' in json_data.keys():
            for item in json_data['area_events']:
                self.area_events.append(Event(item))

    @classmethod
    def get(cls, area_id) -> Optional['Area']:
        return Area._get(f'areas/{area_id}/')

    def __str__(self):
        return self.name
