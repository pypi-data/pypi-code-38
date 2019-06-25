from marshmallow import (
    Schema,
    fields,
)


class DocumentTreeResourceSchema(Schema):
    file_id = fields.Integer(required=True)
    value = fields.Dict(required=True)
    updated_at = fields.DateTime()


class DocumentTreeQueryParamsSchema(Schema):
    file_id = fields.Integer()


class DocumentTreePatchSchema(Schema):
    file_id = fields.Integer(required=True)
    value = fields.Dict(required=True)
