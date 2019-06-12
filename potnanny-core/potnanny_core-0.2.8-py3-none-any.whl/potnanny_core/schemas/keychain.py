from marshmallow import Schema, fields

class KeychainSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    name = fields.Str(
                required=True,
                error_messages={'required': 'name is required'})
    data = fields.Str(
                required=True,
                error_messages={'required': 'data is required'})
