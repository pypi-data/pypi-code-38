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
    app_grp_art_number = fields.String(missing=None)
    country_code = fields.String(missing=None)
    document_number = fields.String(missing=None)
    kind_code = fields.String(missing=None)
    primary_identifier = fields.String(missing=None)
    abstract_text = fields.String(missing=None)
    applicant = fields.String(missing=None)
    inventors = fields.String(missing=None)
    title = fields.String(missing=None)
    url = fields.String(missing=None)
    grant_date = fields.DateTime(missing=None)
    submission_date = fields.DateTime(missing=None)

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
