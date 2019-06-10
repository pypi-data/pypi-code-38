from rest_framework.serializers import Serializer, DecimalField


class LatLongSerializer(Serializer):
    latitude = DecimalField(max_digits=9, decimal_places=6)

    longitude = DecimalField(max_digits=9, decimal_places=6)

    def to_internal_value(self, data):

        if data:
            from django.contrib.gis.geos.point import Point

            return Point(x=data.get("longitude"),
                         y=data.get("latitude"))

    def to_representation(self, instance):
        if instance:
            return {
                "longitude": instance.x,
                "latitude": instance.y
            }
