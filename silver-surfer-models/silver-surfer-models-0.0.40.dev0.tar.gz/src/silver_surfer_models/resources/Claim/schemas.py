from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)


class ClaimResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    patent_id = fields.Integer()
    patent_application_id = fields.Integer()
    claim_number = fields.Integer(required=True)
    claim_text = fields.String(required=True, validate=not_blank)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def pre_load(self, in_data):
        if 'patent_application_id' in in_data and 'patent_id' in in_data:
            raise ValidationError(
                'Cannot provide both '
                '`patent_application_id` and `patent_id` fields'
            )

        if (
            'patent_application_id' not in in_data and
            'patent_id' not in in_data
        ):
            raise ValidationError(
                'Should provide either '
                '`patent_application_id` or `patent_id` field'
            )


class ClaimQueryParamsSchema(Schema):
    id = fields.Integer()
    patent_id = fields.Integer()
    patent_application_id = fields.Integer()
    claim_number = fields.Integer()


class ClaimPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    claim_text = fields.String(validate=not_blank)
