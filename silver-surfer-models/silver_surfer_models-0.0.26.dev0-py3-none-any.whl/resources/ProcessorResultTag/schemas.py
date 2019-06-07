from marshmallow import (
    Schema,
    fields,
    validate,
)


class ProcessorResultTagResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    document_id = fields.Integer(required=True)
    processor_result_id = fields.Integer(required=True)
    processor_name = fields.String(required=True, validate=not_blank)
    tag = fields.String(required=True, validate=not_blank)
    updated_at = fields.DateTime()


class ProcessorResultTagQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    document_id = fields.Integer()
    processor_result_id = fields.Integer()
    processor_name = fields.String(validate=not_blank)
