from marshmallow import (
    Schema,
    fields,
    validate,
)


class AbstractTextResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    patent_id = fields.Integer()
    abstract_text = fields.String()
    updated_at = fields.DateTime()


class AbstractTextQueryParamsSchema(Schema):
    id = fields.Integer()
    patent_id = fields.Integer()


class AbstractTextPatchSchema(Schema):
    abstract_text = fields.String()
