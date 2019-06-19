from marshmallow import (
    Schema,
    fields,
    validate,
)


class InstitutionProbabilityResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    ptab_trial_num = fields.String(required=True, validate=not_blank)
    is_instituted = fields.Boolean()
    probability_of_institution = fields.Float()
    probability_end_before_trial_end = fields.Float()
    probability_of_all_claims_instituted = fields.Float()
    probability_of_some_claims_instituted = fields.Float()

    updated_at = fields.DateTime(dump_only=True)


class InstitutionProbabilityQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    ptab_trial_num = fields.String(validate=not_blank)
