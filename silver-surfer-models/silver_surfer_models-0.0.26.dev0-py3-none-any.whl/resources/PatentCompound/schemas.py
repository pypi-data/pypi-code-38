from marshmallow import (
    Schema,
    fields,
    validate,
)


class PatentCompoundResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    patent_id = fields.Integer(required=True)
    cid = fields.String(validate=not_blank, required=True)
    compound_name = fields.String(required=True)
    iupac_name = fields.String(required=True)
    molecular_formula = fields.String(validate=not_blank, required=True)
    molecular_weight = fields.String(validate=not_blank, required=True)
    structure_file_id = fields.Integer(required=True)
    updated_at = fields.DateTime()


class PatentCompoundQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    patent_id = fields.Integer()
    cid = fields.String(validate=not_blank)
    compound_name = fields.String()
    iupac_name = fields.String(validate=not_blank)
