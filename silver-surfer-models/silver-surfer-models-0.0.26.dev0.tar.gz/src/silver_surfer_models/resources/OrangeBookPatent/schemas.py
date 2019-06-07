from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)

from ...utils.utils import convert_string_to_datetime


def pre_load_helper(in_data):
    try:
        if in_data.get('patent_expire_date'):
            in_data['patent_expire_date'] = convert_string_to_datetime(
                date=in_data['patent_expire_date'],
                string_format='%b %d, %Y',
            )
        else:
            in_data['patent_expire_date'] = None
        if in_data.get('submission_date'):
            in_data['submission_date'] = convert_string_to_datetime(
                date=in_data['submission_date'],
                string_format='%b %d, %Y',
            )
        else:
            in_data['submission_date'] = None
    except (TypeError, ValueError):
        raise ValidationError('Invalid date format')
    return in_data


class OrangeBookPatentResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    appl_no = fields.String(required=True)
    appl_type = fields.String(required=True)
    delist_flag = fields.String(required=True)
    drug_product_flag = fields.String(required=True)
    drug_substance_flag = fields.String(required=True)
    patent_no = fields.String(required=True, validate=not_blank)
    patent_use_code = fields.String(required=True)
    product_no = fields.String(required=True, validate=not_blank)
    patent_expire_date = fields.DateTime(required=True, allow_none=True)
    submission_date = fields.DateTime(required=True, allow_none=True)

    @pre_load
    def pre_load_date_fields(self, in_data):
        return pre_load_helper(in_data)


class OrangeBookPatentQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    appl_no = fields.String(validate=not_blank)
    appl_nos = fields.List(fields.Integer())
    patent_no = fields.String(validate=not_blank)
    product_no = fields.String(validate=not_blank)


class OrangeBookPatentPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    appl_no = fields.String()
    appl_type = fields.String()
    delist_flag = fields.String()
    drug_product_flag = fields.String()
    drug_substance_flag = fields.String()
    patent_no = fields.String(validate=not_blank)
    patent_use_code = fields.String()
    product_no = fields.String(validate=not_blank)
    patent_expire_date = fields.DateTime(allow_none=True)
    submission_date = fields.DateTime(allow_none=True)

    @pre_load
    def pre_load_date_fields(self, in_data):
        return pre_load_helper(in_data)
