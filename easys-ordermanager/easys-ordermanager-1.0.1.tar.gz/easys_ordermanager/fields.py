from rest_framework import serializers
from phonenumbers import NumberParseException, parse, PhoneNumberFormat
from phonenumber_field.phonenumber import PhoneNumber


class PhoneNumberField(serializers.Field):
    number_format = PhoneNumberFormat.NATIONAL

    def __init__(self, number_format=None, *args, **kwargs):
        self.number_format = number_format or self.number_format
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        if not isinstance(value, PhoneNumber):
            try:
                value = parse(value, numobj=PhoneNumber())
            except (NumberParseException, TypeError):
                return value

        return value.format_as(self.number_format).replace(' ', '')

    def to_internal_value(self, data):
        return str(data)
