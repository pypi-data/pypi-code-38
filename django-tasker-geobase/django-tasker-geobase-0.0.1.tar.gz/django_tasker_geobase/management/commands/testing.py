from django.core.management import BaseCommand
from django_tasker_geobase import geocoder


class Command(BaseCommand):
    help = 'Geocoder'

    # https://tech.yandex.ru/maps/geocoder/doc/desc/reference/kind-docpage/

    def handle(self, *args, **options):
        # geocoder.search(query="124.713374, 56.655495")
        #geocoder.search(query="Реутов Комсомольская 32 кв.61")
        #result = geocoder.geo(query="Реутов Комсомольская 32 кв.61")
        # print(result.zipcode)

        # result = geocoder.haversine(
        #     longitude1=37.849392,
        #     latitude1=55.759907,
        #     longitude2=37.855141,
        #     latitude2=55.760515
        # )
        # print(result)

        result = geocoder.ip(ip="77.51.190.21")
        # result = ip.wifi(mac="10:7B:EF:55:99:3A")
        # print(result.get())
