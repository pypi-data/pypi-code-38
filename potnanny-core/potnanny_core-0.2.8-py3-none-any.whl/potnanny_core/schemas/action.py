import json
import copy
import marshmallow
from marshmallow import Schema, fields


class ActionSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    created = fields.DateTime(dump_only=True)
    is_active = fields.Boolean()
    room_id = fields.Integer()
    measurement_type = fields.Str(required=True)
    sensor = fields.Str(required=True)
    plugin = fields.Str(required=True)
    triggers = fields.Nested('TriggerSchema', exclude=['action'], dump_only=True, many=True)


class SingularActionSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    created = fields.DateTime(dump_only=True)
    utc_runtime = fields.DateTime(dump_only=True)
    completed = fields.DateTime(dump_only=True)
    status = fields.Str()
    action = fields.Str(required=True)
