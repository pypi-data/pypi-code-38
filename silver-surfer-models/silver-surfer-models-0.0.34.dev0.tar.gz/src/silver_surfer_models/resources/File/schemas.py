from marshmallow import (
    Schema,
    fields,
    validate,
)


class FileResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    file_format = fields.String(validate=not_blank, required=True)
    s3_bucket_name = fields.String(validate=not_blank, required=True)
    s3_key_name = fields.String(validate=not_blank, required=True)
    content_length = fields.Integer(allow_none=True)
    updated_at = fields.DateTime()


class FileQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    file_format = fields.String(validate=not_blank)
    s3_bucket_name = fields.String(validate=not_blank)
    s3_key_name = fields.String(validate=not_blank)


class FilePatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    file_format = fields.String(validate=not_blank)
    s3_bucket_name = fields.String(validate=not_blank)
    s3_key_name = fields.String(validate=not_blank)
    content_length = fields.Integer(allow_none=True)
