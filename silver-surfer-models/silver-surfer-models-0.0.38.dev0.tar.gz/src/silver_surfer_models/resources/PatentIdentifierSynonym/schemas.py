from marshmallow import (
    Schema,
    fields,
    validate,
)


class PatentIdentifierSynonymResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    patent_id = fields.Integer(required=True)
    synonym = fields.String(validate=not_blank, required=True)
    updated_at = fields.DateTime()


class PatentIdentifierSynonymQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    patent_id = fields.Integer()
    synonym = fields.String(validate=not_blank)
