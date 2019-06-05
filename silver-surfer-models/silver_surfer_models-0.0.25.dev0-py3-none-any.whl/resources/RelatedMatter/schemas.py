from marshmallow import (
    Schema,
    fields,
    pre_load,
    ValidationError,
)


class RelatedMatterResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    document_id = fields.Integer(required=True)
    pacer_case_id = fields.Integer()
    trial_id = fields.Integer()
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def pre_load(self, in_data):
        if 'pacer_case_id' in in_data and 'trial_id' in in_data:
            raise ValidationError(
                'Cannot provide both `pacer_case_id` and `trial_id` fields')

        if 'pacer_case_id' not in in_data and 'trial_id' not in in_data:
            raise ValidationError(
                'Should provide either `pacer_case_id` or `trial_id` field')


class RelatedMatterQueryParamsSchema(Schema):
    id = fields.Integer()
    document_id = fields.Integer()
    pacer_case_id = fields.Integer()
    trial_id = fields.Integer()
