from django.test import TestCase
from django_tasker_geobase import geocoder


class Geobase(TestCase):
    def test_geo(self):
        result = geocoder.geo(query="Новосибирск улица Мира, 61к1 кв.11")
        self.assertEqual(result.zipcode, '630024')
        self.assertEqual(result.longitude, 82.940462)
        self.assertEqual(result.latitude, 54.959423)
        self.assertEqual(result.timezone, 'Asia/Novosibirsk')
        self.assertEqual(result.type, 15)
        self.assertEqual(result.ru, '11')
        self.assertEqual(result.en, '11')



