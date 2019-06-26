from marshmallow import (
    Schema,
    fields,
    validate,
)


class PriorArtResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    ptab2_document_id = fields.Integer(required=True)
    tag = fields.String(required=True, validate=not_blank)
    title = fields.String(required=True, allow_none=True)
    exhibit = fields.String(required=True, allow_none=True)
    updated_at = fields.DateTime()


class PriorArtQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    ptab2_document_id = fields.Integer()
    tag = fields.String(validate=not_blank)


class PriorArtPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    ptab2_document_id = fields.Integer()
    tag = fields.String()
    title = fields.String()
    exhibit = fields.String()
    updated_at = fields.DateTime()
