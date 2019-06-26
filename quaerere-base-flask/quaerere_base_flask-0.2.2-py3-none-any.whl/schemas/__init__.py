__all__ = ['ArangoDBFilterSchema', 'ArangoDBMetadataSchema']

from marshmallow import fields, pre_load, Schema
from werkzeug.datastructures import ImmutableMultiDict


class ArangoDBMetadataSchema(Schema):
    """Schema for ArangoDB insert/update metadata

    :py:attr: `_id` : :py:class: `marshmallow.fields.String` : required=True
        Id of document
    :py:attr: `_key` : :py:class: `~marshmallow.fields.String` : required=True
        Key of document
    :py:attr: `_rev` : :py:class: `~.fields.String` : required=True
        Current revision of document
    :py:attr: `_old_rev` : :py:class: `~.fields.String`
        Previous revision of document

    """
    _id = fields.String(required=True)
    _key = fields.String(required=True)
    _rev = fields.String(required=True)
    _old_rev = fields.String()


class ArangoDBFilterSchema(Schema):
    """

    :py:attr: `filters` : :py:class: `~.fields.List`
        condition
    :py:attr: `variables` : :py:class: `~.fields.Dict`
        variables used to bind
    """
    conditions = fields.List(fields.String(), required=True)
    variables = fields.Dict(required=True)
    _or = fields.Boolean(default=False)
    sort = fields.String()
    limit = fields.Integer()

    @pre_load
    def unwrap_conditions(self, in_data):
        if not isinstance(in_data, ImmutableMultiDict):
            return in_data
        out_data = {
            'conditions': in_data.getlist('condition'),
            'variables': {},
        }
        _or = in_data.get('_or', False)
        sort = in_data.get('sort')
        limit = in_data.get('limit')
        if _or is not None:
            out_data['_or'] = _or
        if sort is not None:
            out_data['sort'] = sort
        if limit is not None:
            out_data['limit'] = limit
        for key in in_data.keys():
            if key in ['condition', 'variables', '_or', 'sort', 'limit']:
                continue
            unlist = in_data.getlist(key)
            if len(unlist) == 1:
                unlist = unlist[0]
            out_data['variables'][key] = unlist
        return out_data
