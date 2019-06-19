from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)

from ...utils.utils import convert_string_to_datetime


class PatentResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    patent_number = fields.String(required=True)
    jurisdiction = fields.String(required=True)
    # `missing` is used during de-serialization (load) and `default` is
    # used during serialization (dump)
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
    grant_date = fields.DateTime()
    submission_date = fields.DateTime()

    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        try:
            if in_data.get('grant_date'):
                in_data['grant_date'] = convert_string_to_datetime(
                    date=in_data['grant_date'],
                    string_format='%Y/%m/%d',
                )
            if in_data.get('submission_date'):
                in_data['submission_date'] = convert_string_to_datetime(
                    date=in_data['submission_date'],
                    string_format='%Y/%m/%d',
                )
        except (TypeError, ValueError):
            raise ValidationError('Invalid date format')
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
