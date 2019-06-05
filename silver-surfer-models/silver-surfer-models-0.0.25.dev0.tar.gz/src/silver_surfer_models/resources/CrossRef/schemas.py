from marshmallow import (
    Schema,
    fields,
    validate,
)


class CrossRefResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    doi = fields.String(required=True, validate=not_blank)
    authors = fields.String(allow_none=True)
    doi_url = fields.String(allow_none=True)
    issn = fields.String(allow_none=True)
    issue = fields.String(allow_none=True)
    journal = fields.String(allow_none=True)
    pages = fields.String(allow_none=True)
    pmid = fields.String(allow_none=True)
    ref_type = fields.String(allow_none=True)
    text = fields.String(allow_none=True)
    title = fields.String(allow_none=True)
    volume = fields.String(allow_none=True)
    year = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)


class CrossRefQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    doi = fields.String(validate=not_blank)
