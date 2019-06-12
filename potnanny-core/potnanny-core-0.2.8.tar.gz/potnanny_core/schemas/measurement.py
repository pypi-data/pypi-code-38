from marshmallow import Schema, fields, validates, ValidationError

class MeasurementSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    type = fields.Str()
    value = fields.Number()
    created = fields.DateTime(dump_only=True)
    sensor_id = fields.Integer()
    sensor = fields.Nested('SensorSchema', dump_only=True)
