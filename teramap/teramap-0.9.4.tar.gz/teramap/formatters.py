from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.geos import Point
from django.utils.html import format_html


class PointFormatter:
    """Returns a nice HTML representation for a django.contrib.gis.geos.Point."""

    html_template = (
        '<span class="teramap-coordinates" title="{long_name}">'
        '<span class="teramap-coordinates-name text-muted">{short_name}</span>&nbsp;'
        '<span class="teramap-coordinates-coords">{point}</span>'
        "</span>"
    )

    INTEGER_FMT = "{p.x:0.0f} {p.y:0.0f}"
    FLOAT_FMT = "{p.x:0.4f}, {p.y:0.4f}"
    LATLNG_FLOAT_FMT = "{p.y:0.4f}, {p.x:0.4f}"

    CONFIG = {
        4326: {"short_name": "GPS", "template": LATLNG_FLOAT_FMT},
        28992: {"short_name": "RDS", "template": INTEGER_FMT},
        31370: {"short_name": "Lambert 1972", "template": INTEGER_FMT},
        "default": {"template": FLOAT_FMT},
    }

    def __init__(self, p, srs=None):
        """
        arguments:
            p (Point): point to display.
            srs (SpatialReference): If not None, point will be tranformed according to srs and displayed using srs.
        """
        if not isinstance(p, Point):
            p = Point(p)

        if not isinstance(srs, SpatialReference):
            try:
                srs = SpatialReference(srs)
            except Exception:
                srs = None

        if srs is not None:
            p = p.transform(srs, clone=True)

        self.p = p

    @property
    def config(self):
        return self.CONFIG.get(self.p.srid, self.CONFIG["default"])

    @property
    def point_template(self):
        return self.config.get("template", self.CONFIG["default"]["template"])

    @property
    def short_name(self):
        return self.config.get("short_name", self.p.srs.name)

    def __str__(self):
        return format_html(
            self.html_template,
            long_name=self.p.srs.name,
            short_name=self.short_name,
            point=self.point_template.format(p=self.p),
        )


def format_point(p, srs=None):
    """Short way to use the PointFormatter class"""
    if p is None or (p.srs is None and srs is None):
        return ""
    return str(PointFormatter(p, srs))
