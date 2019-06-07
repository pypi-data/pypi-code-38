from marshmallow import (
    Schema,
    fields,
)


class ClaimDependencyResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    claim_id = fields.Integer(required=True)
    parent_claim_id = fields.Integer(required=True)
    updated_at = fields.DateTime()


class ClaimDependencyQueryParamsSchema(Schema):
    id = fields.Integer()
    claim_id = fields.Integer()
    parent_claim_id = fields.Integer()
