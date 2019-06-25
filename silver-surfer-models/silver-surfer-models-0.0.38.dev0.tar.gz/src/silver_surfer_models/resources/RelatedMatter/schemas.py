from marshmallow import (
    Schema,
    fields,
    pre_load,
    ValidationError,
)


class RelatedMatterResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    ptab2_document_id = fields.Integer(required=True)
    related_pacer_case_id = fields.Integer()
    related_ptab2_proceeding_id = fields.Integer()
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def pre_load(self, in_data):
        if ('related_pacer_case_id' in in_data and
                'related_ptab2_proceeding_id' in in_data):
            raise ValidationError(
                'Cannot provide both `related_pacer_case_id` and '
                '`related_ptab2_proceeding_id` fields')

        if ('related_pacer_case_id' not in in_data and
                'related_ptab2_proceeding_id' not in in_data):
            raise ValidationError(
                'Should provide either `related_pacer_case_id` or '
                '`related_ptab2_proceeding_id` field')


class RelatedMatterQueryParamsSchema(Schema):
    id = fields.Integer()
    ptab2_document_id = fields.Integer()
    related_pacer_case_id = fields.Integer()
    related_ptab2_proceeding_id = fields.Integer()
