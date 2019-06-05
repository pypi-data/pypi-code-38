from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)

from silver_surfer_models.utils.utils import convert_string_to_datetime


def _pre_load_datetime_fields(in_data):
    date_fields = [
        'document_filing_date',
        'petitioner_grant_date',
        'respondent_grant_date',
    ]

    for date_field in date_fields:
        value = in_data.get(date_field)
        if value:
            if value == '-':
                in_data[date_field] = None
            else:
                in_data[date_field] = convert_string_to_datetime(
                    date=value,
                    string_format='%m-%d-%Y',
                )
        else:
            in_data[date_field] = None

    return in_data


class PTAB2DocumentResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    document_category = fields.String()
    document_filing_date = fields.DateTime(allow_none=True)
    document_identifier = fields.String(required=True)
    document_name = fields.String()
    document_number = fields.String()
    document_size = fields.String()
    document_title_text = fields.String()
    document_type_name = fields.String()
    filing_party_category = fields.String()
    media_type_category = fields.String()
    petitioner_application_number_text = fields.String()
    petitioner_counsel_name = fields.String()
    petitioner_grant_date = fields.DateTime(allow_none=True)
    petitioner_group_art_unit_number = fields.String()
    petitioner_inventor_name = fields.String()
    petitioner_party_name = fields.String()
    petitioner_patent_number = fields.String()
    petitioner_patent_owner_name = fields.String()
    petitioner_technology_center_number = fields.String()
    proceeding_number = fields.String()
    proceeding_type_category = fields.String()
    respondent_application_number_text = fields.String()
    respondent_counsel_name = fields.String()
    respondent_grant_date = fields.DateTime(allow_none=True)
    respondent_group_art_unit_number = fields.String()
    respondent_inventor_name = fields.String()
    respondent_party_name = fields.String()
    respondent_patent_number = fields.String()
    respondent_patent_owner_name = fields.String()
    respondent_technology_center_number = fields.String()
    subproceeding_type_category = fields.String()
    file_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        return _pre_load_datetime_fields(in_data)


class PTAB2DocumentQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    document_identifier = fields.String()
    proceeding_number = fields.String()
