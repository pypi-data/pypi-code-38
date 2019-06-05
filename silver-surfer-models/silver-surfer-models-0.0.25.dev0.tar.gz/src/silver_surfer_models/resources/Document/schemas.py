from marshmallow import (
    Schema,
    fields,
    validate,
)


class DocumentResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    trial_id = fields.Integer(required=True)
    ptab_document_id = fields.Integer(required=True)
    title = fields.String()
    filing_date = fields.DateTime()
    type = fields.String()
    file_id = fields.Integer()
    has_smart_doc = fields.Boolean()
    exhibit_number = fields.String()
    document_number = fields.String()
    is_petition_doc = fields.Boolean()
    updated_at = fields.DateTime(dump_only=True)


class DocumentQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    trial_id = fields.Integer()
    ptab_document_id = fields.Integer()
    document_number = fields.String()
    filing_date = fields.DateTime()
    type = fields.String()
    file_id = fields.Integer(allow_none=True)
    has_smart_doc = fields.Boolean()
    is_petition_doc = fields.Boolean()


class DocumentPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    trial_id = fields.Integer()
    ptab_document_id = fields.Integer()
    title = fields.String()
    filing_date = fields.DateTime()
    type = fields.String()
    file_id = fields.Integer()
    has_smart_doc = fields.Boolean()
    exhibit_number = fields.String()
    document_number = fields.String()
    is_petition_doc = fields.Boolean()
