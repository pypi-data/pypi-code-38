import json


class State(dict):

    def __init__(self, fields: dict, state: dict = None, *args, **kwargs):
        """
        :param fields: is a dictionary that holds the state items. The value of each key is the data type.
        :param state:
        :param args:
        :param kwargs:
        """
        self.fields = fields

        super().__init__(*args, **kwargs)
        if not state:
            state = {}

        for field, conversion in self.fields.items():
            self.set_field_if_exists(field, state, conversion)

    def set_field_if_exists(self, field, state, conversion):
        if not field:
            return

        value = None

        if field in state and state[field] is not None:
            value = state[field]
            if conversion:
                value = conversion(value)

        self[field] = value

    def to_json(self):
        output = {field: self.get(field, None) for field in self.fields.keys()}
        output = json.dumps(output)

        return output

    def get(self, key, default=None):
        value = super().get(key, None)
        if value is None:
            value = default
        return value
