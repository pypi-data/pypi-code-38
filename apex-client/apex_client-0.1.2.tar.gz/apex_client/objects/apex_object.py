from typing import Optional

from dateutil import parser

from apex_client.request import ApexRequest


class ApexObject:
    valid_properties = []
    date_properties = []
    mapped_properties = {}

    def __init__(self, json_data: dict):
        self.dynamic_properties = {}

        for key in self.valid_properties:
            setattr(self, key, json_data.get(key))

        for key in self.mapped_properties.keys():
            setattr(self, self.mapped_properties[key], json_data.get(key))

        if 'dynamic_fields' in json_data:
            for item in json_data['dynamic_fields']:
                self.dynamic_properties[item['property']] = {
                    'value': item['value'],
                    'type': item['type'],
                    'options': item['options']
                }

        for key in self.date_properties:
            if json_data.get(key):
                setattr(self, key, parser.parse(json_data.get(key)))
            else:
                setattr(self, key, None)

    @classmethod
    def _get(cls, path: str) -> Optional['ApexObject']:
        response = ApexRequest.get(path)

        if response['status_code'] == 200:
            return cls(response['response'])

        return None

    def get_dynamic_property(self, key, default_value=None):
        dynamic_property = self.dynamic_properties.get(key)

        if dynamic_property:
            value = dynamic_property.get('value')

            if value is not None:
                return value

        if default_value is not None:
            return default_value

        return None

    def get_dynamic_property_display(self, key):
        dynamic_property = self.dynamic_properties.get(key)

        if dynamic_property:
            value = self.get_dynamic_property(key)

            if value and dynamic_property.get('options') and dynamic_property.get('options').get('choices'):
                for choice in dynamic_property['options']['choices']:
                    if str(choice[0]) == str(value):
                        return choice[1]

        return None

    def has_dynamic_property(self, key) -> bool:
        return self.dynamic_properties.get(key) is not None

    def get_dynamic_fields(self):
        dynamic_fields = []

        for key, dynamic_property in self.dynamic_properties.items():
            dynamic_fields.append({
                'property': key,
                'value': dynamic_property['value']
            })

        return dynamic_fields

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def __repr__(self):
        return f"<{self.__class__.__name__}: {str(self)}>"

    def __str__(self):
        return "Empty class"

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)

        except AttributeError as e:
            if name in self.date_properties or name in self.valid_properties:
                return None
            else:
                raise e
