from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)

from ...utils.utils import pre_load_date_fields


class PatentResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    patent_number = fields.String(required=True)
    jurisdiction = fields.String(required=True)
    app_grp_art_number = fields.String()
    country_code = fields.String()
    document_number = fields.String()
    kind_code = fields.String()
    primary_identifier = fields.String()
    abstract_text = fields.String()
    applicant = fields.String()
    inventors = fields.String()
    title = fields.String()
    url = fields.String()
    grant_date = fields.DateTime(allow_none=True)
    submission_date = fields.DateTime(allow_none=True)
    app_status_date = fields.DateTime(allow_none=True)
    app_early_pub_date = fields.DateTime(allow_none=True)
    pto_adjustments = fields.String()
    appl_delay = fields.String()
    total_pto_days = fields.String()
    assignee = fields.String()

    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = [
            'grant_date',
            'submission_date',
            'app_status_date',
            'app_early_pub_date',
        ]
        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y/%m/%d',
        )
        return in_data


class PatentQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    patent_number = fields.String()
    app_grp_art_number = fields.String(validate=not_blank)
    jurisdiction = fields.String(validate=not_blank)
    primary_identifier = fields.String(validate=not_blank)
    applicant = fields.String(validate=not_blank)
    inventors = fields.String(validate=not_blank)
