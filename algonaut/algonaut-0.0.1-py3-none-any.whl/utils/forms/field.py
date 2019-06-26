import datetime

class Field:

    default_validators = []

    @property
    def validators(self):
        return self.default_validators + self._validators

    def __init__(self, validators=None):
        if validators is None:
            validators = []
        self._validators = validators
    
    def validate(self, name, value, form):
        for validator in self.validators:
            result = validator(name, value, form)
            if result is None:
                errors, stop = [], False
            else:
                errors, value, stop = result
            if errors:
                return errors, value
            if stop:
                return [], value
        return [], value
