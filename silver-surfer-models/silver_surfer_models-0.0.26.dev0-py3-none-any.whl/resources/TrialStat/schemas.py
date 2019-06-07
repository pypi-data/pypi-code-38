from marshmallow import (
    Schema,
    fields,
    validate,
)


class TrialStatResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    stat_type = fields.String(required=True, validate=not_blank)
    name = fields.String(required=True, validate=not_blank)
    ref_counts_by_type = fields.String()
    id_count = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)


class TrialStatQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    stat_type = fields.String(validate=not_blank)
    name = fields.String(validate=not_blank)
