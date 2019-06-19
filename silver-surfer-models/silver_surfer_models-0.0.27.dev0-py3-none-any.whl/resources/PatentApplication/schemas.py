from marshmallow import (
    Schema,
    fields,
    validate,
)


class PatentApplicationResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    application_number = fields.String(required=True)
    jurisdiction = fields.String(required=True)
    # `missing` is used during de-serialization (load) and `default` is
    # used during serialization (dump)
    abstract_text = fields.String(missing=None)
    filed_date = fields.DateTime(missing=None)
    inventors = fields.String(missing=None)
    title = fields.String(missing=None)
    updated_at = fields.DateTime(dump_only=True)


class PatentApplicationQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    application_number = fields.String(validate=not_blank)
    jurisdiction = fields.String(validate=not_blank)
