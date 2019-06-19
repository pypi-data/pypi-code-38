from marshmallow import (
    Schema,
    fields,
)


class ClaimChallengedResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    trial_id = fields.Integer(required=True)
    claim_id = fields.Integer(required=True)
    prior_art_combination = fields.Integer(required=True)
    prior_art_id = fields.Integer(required=True)
    prior_art_nature = fields.String(required=True, allow_none=True)
    updated_at = fields.DateTime()


class ClaimChallengedQueryParamsSchema(Schema):
    id = fields.Integer()
    trial_id = fields.Integer()
    claim_id = fields.Integer()
    prior_art_combination = fields.Integer()
    prior_art_id = fields.Integer()
    prior_art_nature = fields.String()
