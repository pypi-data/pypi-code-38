from marshmallow import (
    Schema,
    fields,
    validate,
)


class CompanyResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    applicant_full_name = fields.String(required=True, validate=not_blank)
    exchange = fields.String()
    parent_company = fields.String()
    ticker = fields.String()
    updated_at = fields.DateTime(dump_only=True)


class CompanyQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    applicant_full_name = fields.String(validate=not_blank)
    parent_company = fields.String(validate=not_blank)
    ticker = fields.String(validate=not_blank)
