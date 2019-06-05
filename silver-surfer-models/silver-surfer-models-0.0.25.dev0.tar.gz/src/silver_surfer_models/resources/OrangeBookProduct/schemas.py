from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)

from ...utils.utils import convert_string_to_datetime


def pre_load_helper(in_data):
    try:
        if in_data.get('approval_date'):
            in_data['approval_date'] = convert_string_to_datetime(
                date=in_data['approval_date'],
                string_format='%b %d, %Y',
            )
        else:
            in_data['approval_date'] = None
    except (TypeError, ValueError):
        in_data['approval_date'] = None
    return in_data


class OrangeBookProductResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    appl_no = fields.String(required=True, validate=not_blank)
    appl_type = fields.String(required=True)
    applicant = fields.String(required=True)
    applicant_full_name = fields.String(required=True)
    approval_date = fields.DateTime(required=True, allow_none=True)
    dosage_form = fields.String(required=True)
    ingredient = fields.String(required=True)
    product_no = fields.String(required=True, validate=not_blank)
    rld = fields.String(required=True)
    rs = fields.String(required=True)
    route_of_administration = fields.String(required=True)
    strength = fields.String(required=True)
    te_code = fields.String(required=True)
    trade_name = fields.String(required=True)
    type = fields.String(required=True)

    @pre_load
    def pre_load_date_fields(self, in_data):
        return pre_load_helper(in_data)


class OrangeBookProductQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    appl_no = fields.String(validate=not_blank)
    product_no = fields.String(validate=not_blank)
    trade_name = fields.String(validate=not_blank)


class OrangeBookProductPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    appl_no = fields.String(validate=not_blank)
    appl_type = fields.String()
    applicant = fields.String()
    applicant_full_name = fields.String()
    approval_date = fields.DateTime(allow_none=True)
    dosage_form = fields.String()
    ingredient = fields.String()
    product_no = fields.String(validate=not_blank)
    rld = fields.String()
    rs = fields.String()
    route_of_administration = fields.String()
    strength = fields.String()
    te_code = fields.String()
    trade_name = fields.String()
    type = fields.String()

    @pre_load
    def pre_load_date_fields(self, in_data):
        return pre_load_helper(in_data)
