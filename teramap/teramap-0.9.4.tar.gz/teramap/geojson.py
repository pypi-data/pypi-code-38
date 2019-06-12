import itertools
import json

from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe

from .utils import Accessor, attr_or_key, json_serial, round_geom

# Assume 1 degree = 115 km = 115000 m, simplify to 25m
DEFAULT_SIMPLIFY = getattr(settings, "GEOJSON_DEFAULT_SIMPLIFY", 25 / 115000)


class FeatureBase:
    def __len__(self):
        return len(self.features)

    def len(self):
        # length function to use in templates
        return self.__len__()

    def union(self, other):
        key = "collection_properties"
        properties = {}
        properties.update(getattr(self, key, None) or {})
        properties.update(getattr(other, key, None) or {})

        return FeatureCollection(
            itertools.chain(self.features, other.features),
            collection_properties=properties if len(properties) > 0 else None,
        )

    # support adding two Features/FeatureCollections:
    # geojson = geojson_a + geojson_b
    # geojson += a
    __add__ = union
    __iadd__ = union


class FeatureCollection(FeatureBase):
    def __init__(self, features, collection_properties=None):
        self.features = list(features)
        self.collection_properties = collection_properties

    def to_geojson(self):
        ret = {
            "type": "FeatureCollection",
            "features": [
                feature.to_geojson() if isinstance(feature, Feature) else feature for feature in self.features
            ],
        }
        if getattr(self, "collection_properties", None):
            ret["properties"] = self.collection_properties

        return ret

    def to_geojson_str(self, indent=None):
        return json.dumps(self.to_geojson(), indent=indent, default=json_serial)

    def __str__(self):
        return mark_safe(str(self.to_geojson_str()))


class Feature(FeatureBase):
    @property
    def features(self):
        return (self,)

    def to_geojson(self):
        return {
            "type": "Feature",
            "properties": self.properties,
            "geometry": {"type": self.geom_type, "coordinates": self.coords},
        }


class Point(Feature):
    geom_type = "Point"

    def __init__(self, coords, properties=None):
        self.coords = coords
        self.properties = properties or {}


class LineString(Point):
    geom_type = "LineString"


class TransformToPoint:
    """
    Mixin to convert non-point geometries to a point.

    Useful to present lots of polygons as markers to reduce page load time.
    """

    def geometry(self, obj):
        geom = super().geometry(obj)

        if geom.geom_typeid > 0:
            geom = geom.centroid
        return geom


class GeoJSON(FeatureCollection):
    """
    Transform a list of Models to GeoJSON with properties according to specification.

    Arguments:
        data: list of dicts or QuerySet.
        extra_properties: dict of the same structure as the properties property to add to get_properties
            dict for this instance.
        geom_field: name of the field to use as the geometry, overriding the `geom_field` attribute.
    """

    properties = {"id": "pk"}
    geom_field = "geom"
    precision = 6
    simplify = DEFAULT_SIMPLIFY

    def __init__(self, data, extra_properties=None, geom_field=None):
        self.data = data or []

        self.extra_properties = extra_properties or {}

        if geom_field is not None:
            self.geom_field = geom_field

    def get_properties(self, obj):
        properties = self.properties
        properties.update(self.extra_properties)

        ret = {}

        for key, lookup in properties.items():
            if isinstance(lookup, bool):
                ret[key] = lookup
            elif callable(lookup):
                ret[key] = lookup(obj)
            else:
                ret[key] = Accessor(lookup).resolve(obj)

        return ret

    def geometry(self, obj):
        """
        Return the geometry simplified according to the current simplification setting.
        """
        geom = Accessor(self.geom_field).resolve(obj)
        return geom.simplify(self.simplify, preserve_topology=True)

    def feature(self, obj):
        try:
            geom = self.geometry(obj)
        except AttributeError:
            return None

        return {
            "type": "Feature",
            "properties": self.get_properties(obj),
            "geometry": {"type": geom.geom_type, "coordinates": round_geom(geom.coords, self.precision)},
        }

    @property
    def features(self):
        """
        Return the GeoJSON representation of the list of locations.
        """
        if not hasattr(self, "_features"):
            self._features = []
            for location in self.data:
                feature = self.feature(location)
                if feature:
                    self._features.append(feature)

        return self._features

    def url(self, obj):
        return reverse(self.url_name, kwargs={"pk": attr_or_key(obj, "pk")})
