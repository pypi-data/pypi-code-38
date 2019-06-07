from marshmallow import (
    Schema,
    fields,
    validate,
)


class PacerCaseResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    case_no = fields.String(required=True, validate=not_blank)
    court_id = fields.String(required=True, validate=not_blank)
    pacer_case_external_id = fields.String(required=True, validate=not_blank)
    cause = fields.String()
    county = fields.String()
    defendant = fields.String()
    disposition = fields.String()
    filed_date = fields.DateTime(allow_none=True)
    flags = fields.String()
    jurisdiction = fields.String()
    lead_case = fields.String()
    nature_of_suit = fields.String()
    office = fields.String()
    plaintiff = fields.String()
    related_case = fields.String()
    terminated_date = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)


class PacerCaseQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    ids = fields.List(fields.Integer())
    case_no = fields.String()
    court_id = fields.String()
    pacer_case_external_id = fields.String()


class PacerCasePatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    case_no = fields.String(validate=not_blank)
    court_id = fields.String(required=True, validate=not_blank)
    pacer_case_external_id = fields.String(required=True, validate=not_blank)
    cause = fields.String()
    county = fields.String()
    defendant = fields.String()
    filed_date = fields.DateTime()
    flags = fields.String()
    jurisdiction = fields.String()
    lead_case = fields.String()
    nature_of_suit = fields.String()
    office = fields.String()
    plaintiff = fields.String()
    related_case = fields.String()
