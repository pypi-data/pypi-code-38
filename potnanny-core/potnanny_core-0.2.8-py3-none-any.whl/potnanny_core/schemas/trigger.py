import datetime
from marshmallow import Schema, fields

class TriggerSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    created = fields.DateTime(dump_only=True)
    closed = fields.DateTime()
    notes = fields.Text()

    
