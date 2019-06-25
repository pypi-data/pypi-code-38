from datetime import date, datetime

from django.contrib.gis.geos import Point
from django.utils.encoding import force_text
from django.utils.functional import Promise


def round_geom(geom, precision):
    if isinstance(geom[0], (list, tuple)):
        return [round_geom(p, precision) for p in geom]

    return [round(l, precision) for l in geom]


def geom_accuracy(geom, point_accuracy=10):
    """
    Approximation of the 'radius' of a geometry in meters

    Done by taking the max distance between centroid and each of the coordinates.

    In case of a point, `point_accuracy` is used, which defaults to 10.
    """
    if geom.dims == 0:
        return point_accuracy
    elif geom.dims == 1:
        coords = geom.coords
    else:
        coords = geom.coords[0]
    centroid = geom.centroid
    return int(max([centroid.distance(Point(p)) for p in coords]) * 115200)


# simplified version of the implementation in
# https://github.com/jieter/django-tables2/blob/master/django_tables2/utils.py#L274
class Accessor(str):
    SEPARATOR = "."

    @property
    def bits(self):
        if self == "":
            return ()

        if self.SEPARATOR not in self:
            return self.split("__")

        return self.split(self.SEPARATOR)

    def resolve(self, context, safe=True):
        if isinstance(context, dict):
            return context[self]

        current = context
        for bit in self.bits:
            try:  # dictionary lookup
                current = current[bit]
            except (TypeError, AttributeError, KeyError):
                try:  # attribute lookup
                    current = getattr(current, bit)
                except (TypeError, AttributeError):
                    try:  # list-index lookup
                        current = current[int(bit)]
                    except (
                        IndexError,  # list index out of range
                        ValueError,  # invalid literal for int()
                        KeyError,  # dict without `int(bit)` key
                        TypeError,  # unsubscriptable object
                    ):
                        raise ValueError(
                            "Failed lookup for key [%s] in %r, " "when resolving the accessor %s" % (bit, current, self)
                        )

            if callable(current):
                if safe and getattr(current, "alters_data", False):
                    raise ValueError("refusing to call %s() because `.alters_data = True`" % repr(current))
                if not getattr(current, "do_not_call_in_templates", False):
                    current = current()
            # important that we break in None case, or a relationship
            # spanning across a null-key will raise an exception in the
            # next iteration, instead of defaulting.
            if current is None:
                break
        return current


def attr_or_key(obj, lookup):
    """Get an attribute if it exists on the object, else treat obj as dict"""
    return Accessor(lookup).resolve(obj)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, Promise):
        return force_text(obj)

    raise TypeError("Type %s not serializable" % type(obj))
