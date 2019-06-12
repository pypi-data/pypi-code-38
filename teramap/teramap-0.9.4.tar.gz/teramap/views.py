from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.gzip import gzip_page

from .geojson import GeoJSON


class GeoJSONView(View):
    """
    Return a GeoJSON for the object list.

    Example:

    class View(teramap.GeoJSONView, ListView):
        GeoJSONClass = LocationGeoJSON
        model = Location

    """

    GeoJSONClass = GeoJSON

    def __init__(self, *args, **kwargs):
        class Klass(self.GeoJSONClass):
            pass

        if hasattr(self, "geom_field"):
            Klass.geom_field = self.geom_field
        if hasattr(self, "get_properties"):
            Klass.get_properties = lambda obj: self.get_properties(obj)

        self.geojson = Klass([])

        super().__init__(*args, **kwargs)

    @method_decorator(gzip_page)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_data(self, context):
        try:
            return context["object_list"]
        except KeyError:
            pass

        try:
            return [context["object"]]
        except KeyError:
            pass

        return []

    def render_to_response(self, context, **response_kwargs):
        self.geojson.data = self.get_data(context)

        return JsonResponse(self.geojson.to_geojson())
