from marshmallow import (
    Schema,
    fields,
    validate,
    ValidationError,
    pre_load,
)
from ...utils.utils import convert_string_to_datetime


def _pre_load_datetime_fields(in_data):
    try:
        if in_data.get('trial_filing_date'):
            in_data['trial_filing_date'] = convert_string_to_datetime(
                in_data['trial_filing_date'],
            )
        if in_data.get('accorded_filing_date'):
            in_data['accorded_filing_date'] = convert_string_to_datetime(
                in_data['accorded_filing_date'],
            )
        else:
            in_data['accorded_filing_date'] = None
        if in_data.get('institution_decision_date'):
            in_data['institution_decision_date'] = convert_string_to_datetime(
                in_data['institution_decision_date'],
            )
        else:
            in_data['institution_decision_date'] = None
    except (TypeError, ValueError):
        raise ValidationError('Invalid format: filing date')
    return in_data


class TrialResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    ptab_trial_num = fields.String(validate=not_blank, required=True)
    trial_filing_date = fields.DateTime(required=True)
    patent_num = fields.String(validate=not_blank, required=True)
    accorded_filing_date = fields.DateTime(allow_none=True)
    institution_decision_date = fields.DateTime(allow_none=True)
    application_number = fields.String(allow_none=True)
    inventor_name = fields.String(allow_none=True)
    patent_owner_name = fields.String(allow_none=True)
    petitioner_party_name = fields.String(allow_none=True)
    prosecution_status = fields.String(allow_none=True)
    is_cleaned = fields.Boolean()
    is_processed = fields.Boolean()
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        return _pre_load_datetime_fields(in_data)


class TrialQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    ids = fields.List(fields.Integer())
    ptab_trial_num = fields.String(validate=not_blank)
    trial_filing_date = fields.DateTime()
    patent_num = fields.String()
    patent_nums = fields.List(fields.String())
    is_cleaned = fields.Boolean()
    is_processed = fields.Boolean()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        return _pre_load_datetime_fields(in_data)


class TrialPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    ptab_trial_num = fields.String(validate=not_blank)
    trial_filing_date = fields.DateTime()
    patent_num = fields.String()
    accorded_filing_date = fields.DateTime(allow_none=True)
    institution_decision_date = fields.DateTime(allow_none=True)
    application_number = fields.String(allow_none=True)
    inventor_name = fields.String(allow_none=True)
    patent_owner_name = fields.String(allow_none=True)
    petitioner_party_name = fields.String(allow_none=True)
    prosecution_status = fields.String(allow_none=True)
    is_cleaned = fields.Boolean()
    is_processed = fields.Boolean()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        return _pre_load_datetime_fields(in_data)
