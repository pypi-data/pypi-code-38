from marshmallow import (
    Schema,
    fields,
    pre_load,
    ValidationError,
)


class PriorArtRefRelationResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    prior_art_id = fields.Integer(required=True)
    cross_ref_id = fields.Integer()
    patent_id = fields.Integer()
    patent_application_id = fields.Integer()
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def pre_load(self, in_data):
        if self._get_number_of_ref_fields(in_data) != 1:
            raise ValidationError('Provide only one of the ref fields')

    def _get_number_of_ref_fields(self, in_data):
        result = 0
        if 'cross_ref_id' in in_data:
            result += 1
        if 'patent_id' in in_data:
            result += 1
        if 'patent_application_id' in in_data:
            result += 1
        return result


class PriorArtRefRelationQueryParamsSchema(Schema):
    id = fields.Integer()
    prior_art_id = fields.Integer()
    cross_ref_id = fields.Integer()
    patent_id = fields.Integer()
    patent_application_id = fields.Integer()
