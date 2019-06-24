# -*- coding: utf-8 -*-
from pyramid.view import view_defaults, view_config
from oe_geoutils.utils import check_in_flanders, check_within_flanders, nearest_location
from pyramid.httpexceptions import HTTPBadRequest
import colander
import json
from pyramid.response import Response


class ValidationFailure(Exception):
    '''
    Custom Exception for data validation errors.
    '''

    def __init__(self, msg, errors):
        self.msg = msg
        self.errors = errors


@view_defaults(renderer='json', accept='application/json')
class View(object):
    def __init__(self, request):
        self.request = request
        self.request_LOCALE_ = 'nl'

    def _retrieve_json(self):
        if self.request.body and not self.request.body == '':
            return self.request.json_body
        else:
            raise HTTPBadRequest("request has no body")

    def validate_geojson(self, params):
        max_area = int(self.request.registry.settings.get('oe_geoutils.max_area', 8000))
        from oe_geoutils.validation.validators_contour import (
            GeometrieSchemaNode as geometrie_schema
        )
        try:
            return geometrie_schema(max_area).deserialize(params)
        except colander.Invalid as e:
            raise ValidationFailure(
                    'De geojson geometrie is niet geldig.',
                    e.asdict(translate=self.request.localizer.translate)
            )

    @view_config(route_name='nearest_address')
    def nearest_address(self):
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        if check_in_flanders(geojson_input):
            crab_gateway = self.request.crab_gateway() if hasattr(self.request, 'crab_gateway') else None
            address = nearest_location(geojson_input, crab_gateway)
            if address is None:
                return {"found": False}
            return {"found": True, "address": address}
        else:
            raise ValidationFailure(
                    "De geojson geometrie is niet geldig.",
                    {"": "Geometrie ligt niet binnen Vlaanderen"}
            )

    @view_config(route_name='check_in_flanders')
    def check_in_flanders(self):
        try:
            check_getijdezone = int(self.request.params.get('check_getijdezone', 0))
        except ValueError:
            raise HTTPBadRequest(
                detail='Request parameter "getijdezone" moet een numerieke waarde zijn (0 of 1).')
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        return {'IntersectFlanders': check_in_flanders(geojson_input, check_getijdezone)}

    @view_config(route_name='check_within_flanders')
    def check_within_flanders(self):
        try:
            tolerance = int(self.request.params.get('tolerance', 10))
        except ValueError:
            raise HTTPBadRequest(detail='Request parameter "tolerance" moet een numerieke waarde zijn.')
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        return {'WithinFlanders': check_within_flanders(geojson_input, tolerance)}

    @view_config(route_name='gemeente')
    def gemeente_niscode(self):
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        return self.request.registry.admin_grenzen_client.get_gemeente(geojson_input)

    @view_config(route_name='provincie')
    def provincie_niscode(self):
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        return self.request.registry.admin_grenzen_client.get_provincie(geojson_input)

    @view_config(route_name='check_in_erfgoedgemeente')
    def check_erfgoedgemeente(self):
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        erfgoedgemeenten_body = self.request.registry.admin_grenzen_client.check_erfgoedgemeenten(
            geojson_input, self.request.registry.settings['erfgoedgemeenten'])
        return Response(json.dumps(erfgoedgemeenten_body),
                        content_type='application/json', status=200, charset='utf-8')
