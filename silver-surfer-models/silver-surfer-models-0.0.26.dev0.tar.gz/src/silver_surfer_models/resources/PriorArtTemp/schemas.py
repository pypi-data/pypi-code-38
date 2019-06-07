from marshmallow import (
    Schema,
    fields,
    validate,
)


class PriorArtTempResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    prior_art_id = fields.Integer(required=True)
    prior_art_detail = fields.String(required=True)
    updated_at = fields.DateTime()


class PriorArtTempQueryParamsSchema(Schema):
    id = fields.Integer()
    prior_art_id = fields.Integer()


class PriorArtTempPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    prior_art_detail = fields.String()
