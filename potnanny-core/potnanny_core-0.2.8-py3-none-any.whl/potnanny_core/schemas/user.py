from marshmallow import Schema, fields

class UserSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str()
    created = fields.DateTime(dump_only=True)
    is_active = fields.Boolean()
