from marshmallow import (
    Schema,
    fields,
    validate,
)


class ProcessorResultResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    document_id = fields.Integer(required=True)
    processor_name = fields.String(required=True, validate=not_blank)
    result = fields.String(required=True, validate=not_blank)
    updated_at = fields.DateTime()


class ProcessorResultQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    document_id = fields.Integer()
    processor_name = fields.String(validate=not_blank)
