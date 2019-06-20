# -*- coding: utf-8 -*-
'''
This module validates a polygon in Flanders.
'''

import colander
import json
from shapely.geometry import shape, box, mapping
from oe_geoutils.utils import get_srid_from_geojson, remove_dupl_coords
import logging
import sys

log = logging.getLogger(__name__)


class GeometryValidator:

    def __init__(self, node, gj):
        """
        :param node: A colander SchemaNode.
        :param gj: geojson to be validated
        """
        self.node = node
        self.gj = gj
        if self.gj is None or not self.gj:
            raise colander.Invalid(self.node, "geometrie is verplicht en mag niet leeg zijn")
        try:
            self.geom = shape(self.gj)
        except ValueError:
            raise colander.Invalid(self.node, 'geometrie is geen geldig GeoJson')
        self.srid = get_srid_from_geojson(self.gj)

    def _validate_geometry_type(self, geomtype):
        """
        :param geomtype: geojson geometrie type: "MultiPolygon", "Point", ...
        :return:
        """
        if self.geom.type != geomtype:
            raise colander.Invalid(self.node, 'geometrie is niet van het type {}'.format(geomtype))

    def _validate_flanders_specifications(self):
        """
        *coordinate system of Lambert72 is required
        *geometry must be inside bounding box of Flanders
        """
        if self.srid is None or self.srid != 31370:
            raise colander.Invalid(self.node,
                                   'Geen geldige srid gevonden. '
                                   'Enkel geometrien met srid 31370 (Lambert 72) worden ondersteund')
        b = box(19680.692555495727, 146642.51885241456, 274994.53266103653,
                245606.4642544454)  # bounding box vlaanderen
        if not b.contains(self.geom):
            message = 'Geometrie ligt niet binnen de bounding box van Vlaanderen. ' \
                      'Controleer ook of je het Lambert72 coördinatensysteem gebruikt.'
            if sys.version_info < (3, 0):
                message = unicode(message.decode("utf-8"))
            raise colander.Invalid(self.node, message)

    def validate_multipolygon(self, max_area):
        """
        Validate a geojson if it is a valid geometry.
        :param max_area: the maximum area of the geojson.
        Current checks are:
        *geojson geometrie type: "MultiPolygon"
        *coordinate system of Lambert72 is required
        *geometry must be inside bounding box of Flanders
        *point must be valid according to OGC-specifications
        *geometry must be smaller than the given max_area

        :raise colander.Invalid: when geojson does not satisfy the upper conditions
        """
        self._validate_geometry_type("MultiPolygon")
        self._validate_flanders_specifications()
        if self.geom.is_empty or not self.geom.is_valid or not self.geom.is_simple:
            self.geom = self.geom.buffer(0)
            if self.geom.is_empty or not self.geom.is_valid or not self.geom.is_simple:
                raise colander.Invalid(self.node,
                                       'Geometrie is niet geldig '
                                       '(bv: leeg, voldoet niet aan OGC, zelf-intersecterend,...)')
            self.gj.update(json.loads(json.dumps(mapping(self.geom))))
            if self.gj['type'] == 'Polygon':
                self.gj.update({'type': 'MultiPolygon', 'coordinates': [self.gj['coordinates']]})
        if self.geom.area > max_area:
            raise colander.Invalid(self.node,
                                              'De oppervlakte van de getekende zone is te groot.'
                                              'De huidige zone is {} ha, maar mag maximum {} ha zijn. '
                                              'Gelieve de zone opnieuw in te tekenen.'.format(self.geom.area / 10000,
                                                                                          max_area / 10000))
        # remove duplicate consecutive coordinates (OGC SFA en ISO 19107:2003 standard)
        remove_dupl_coords(self.gj["coordinates"])
        return self.gj

    def validate_point(self):
        """
        Validate a geojson if it is a valid point.
        Current checks are:
        *Type of geometry must be "Point"
        *coordinate system of Lambert72 is required
        *geometry must be inside bounding box of Flanders
        :param node: A colander SchemaNode.
        :param gj: geojson to be validated
        :raise colander.Invalid: when geojson does not satisfy the upper conditions
        """
        self._validate_geometry_type("Point")
        self._validate_flanders_specifications()
        return self.gj

    def validate_multipoint(self):
        """
        Validate a geojson if it is a valid multi point.
        Current checks are:
        *Type of geometry must be "MultiPoint"
        *coordinate system of Lambert72 is required
        *geometry must be inside bounding box of Flanders
        :param node: A colander SchemaNode.
        :param gj: geojson to be validated
        :raise colander.Invalid: when geojson does not satisfy the upper conditions
        """
        self._validate_geometry_type("MultiPoint")
        self._validate_flanders_specifications()
        return self.gj


class GeoJson(colander.SchemaType):
    """ GeoJson object Type """

    def serialize(self, node, appstruct):
        raise NotImplementedError()

    def deserialize(self, node, cstruct):
        if cstruct != 0 and not cstruct:
            return colander.null
        try:
            return self.build_shape(cstruct)
        except Exception:
            raise colander.Invalid(node, "Geen geldige GeoJson: %s" % cstruct)

    @staticmethod
    def build_shape(cstruct):
        """
        converts a value into GeoJson (if valid)
        raises a colander.Invalid if value cannot be transformed into GeoJson
        :param cstruct: The structure to be validated
        :return: geojson
        :raise colander.Invalid: when the value is no valid geojson
        """
        if cstruct is None or not cstruct:
            return None
        s = json.dumps(cstruct)
        g1 = json.loads(s)
        shape(g1)
        return g1


class GeometrieSchemaNode(colander.SchemaNode):
    title = 'geometrie'
    schema_type = GeoJson
    max_area = 8000

    def __init__(self, *args, **kwargs):
        if len(args) > 0 and isinstance(args[0], int):
            self.max_area = args[0]
            args = args[1:]
        super(GeometrieSchemaNode, self).__init__(*args, **kwargs)
        try:
            self.max_area = float(self.max_area) * 10000
        except ValueError:
            log.error("oe_geoutils: invalid configuration for max area geometry: {}".format(self.max_area))
            self.max_area = 80000000

    def validator(self, node, cstruct):
        return GeometryValidator(node, cstruct).validate_multipolygon(self.max_area)


class PointGeometrieSchemaNode(colander.SchemaNode):
    title = 'point geometrie'
    schema_type = GeoJson

    def validator(self, node, cstruct):
        return GeometryValidator(node, cstruct).validate_point()


class MultiPointGeometrieSchemaNode(colander.SchemaNode):
    title = 'multi point geometrie'
    schema_type = GeoJson

    def validator(self, node, cstruct):
        return GeometryValidator(node, cstruct).validate_multipoint()
