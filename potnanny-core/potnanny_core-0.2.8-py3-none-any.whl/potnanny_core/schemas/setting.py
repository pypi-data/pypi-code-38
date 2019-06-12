from marshmallow import Schema, fields, validates, ValidationError

class PollingIntervalSchema(Schema):
    class META:
        strict = True

    minutes = fields.Integer(required=True)


class TemperatureDisplaySchema(Schema):
    class META:
        strict = True

    display = fields.Str(required=True)

    @validates('display')
    def validate_choice(self, value):
        if value not in ['celsius', 'fahrenheit']:
            raise ValidationError('Choice must be "celsius" or "fahrenheit"')


class PrimitiveWirelessSettingSchema(Schema):
    class META:
        strict = True

    transmit_pin = fields.Integer(required=True)
    receive_pin = fields.Integer(required=True)
    pulse_width = fields.Integer(required=True)
    rf_send = fields.Str(required=True)
    rf_scan = fields.Str(required=True)


class VesyncAccountSchema(Schema):
    class META:
        strict = True

    username = fields.Str(required=True)
    password = fields.Str(required=True)
