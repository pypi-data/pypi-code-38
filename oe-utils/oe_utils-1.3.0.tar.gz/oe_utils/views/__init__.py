# -*- coding: utf-8 -*-
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPNotFound
)

import colander

from oe_utils.validation import ValidationFailure


def get_resource(data_manager, resource_id, detail="No details provided."):
    resource = data_manager.get(resource_id)
    if not resource:
        raise HTTPNotFound(detail=detail)
    return resource


def get_json_from_request(request):
    try:
        return request.json_body
    except AttributeError as e:
        raise HTTPBadRequest(detail="Request bevat geen json body. \n%s" % e)
    except ValueError as e:   # pragma no cover
        raise HTTPBadRequest(detail="Request bevat incorrecte json body. \n%s" % e)   # pragma no cover


def validate(request, json_data, mapping_schema):
    validaton_schema = mapping_schema.bind(request=request)
    try:
        return validaton_schema.deserialize(json_data)
    except colander.Invalid as e:
        raise ValidationFailure('Fouten bij het valideren van request.', e.asdict())


class RouteConfigArgs:
    def __init__(self, response_schemas, schema=None, permission=None,
                 tags=None, protected=False, **kwargs):
        self.tags = tags
        self.response_schemas = response_schemas
        self.schema = schema
        self.permission = permission
        if protected:
            kwargs['protected'] = protected
        self.__dict__.update(kwargs)


class RouteConfig:
    def __init__(self, service, get_args=None, post_args=None, put_args=None, delete_args=None):
        self.service = service
        self.get_args = get_args
        self.post_args = post_args
        self.put_args = put_args
        self.delete_args = delete_args

    @property
    def post(self):
        return self.service.post(**self.post_args.__dict__)

    @property
    def get(self):
        return self.service.get(**self.get_args.__dict__)

    @property
    def put(self):
        return self.service.put(**self.put_args.__dict__)

    @property
    def delete(self):
        return self.service.delete(**self.delete_args.__dict__)

    @property
    def get_validation_scheme(self):
        return self.get_args.schema.__class_schema_nodes__[-1]

    @property
    def put_validation_scheme(self):
        return self.put_args.schema.__class_schema_nodes__[-1]

    @property
    def post_validation_scheme(self):
        return self.post_args.schema.__class_schema_nodes__[-1]
