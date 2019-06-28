from django.test import TestCase

from drc_cmis.client.mapper import mapper, reverse_mapper


class MapperTests(TestCase):
    def test_mapper_get_document(self):
        self.assertEqual(mapper('identificatie'), 'drc:document__identificatie')
        self.assertEqual(mapper('identificatie', 'document'), 'drc:document__identificatie')

    def test_mapper_get_connection(self):
        self.assertEqual(mapper('object', 'connection'), 'drc:connectie__zaakurl')

    def test_mapper_get_zaaktype(self):
        self.assertEqual(mapper('identificatie', 'zaaktype'), 'drc:zaaktype__identificatie')

    def test_mapper_get_zaak(self):
        self.assertEqual(mapper('identificatie', 'zaak'), 'drc:zaak__identificatie')

    def test_mapper_get_unknown(self):
        self.assertIsNone(mapper('identificatie', 'unknown'))


class ReverseMapperTests(TestCase):
    def test_mapper_get_document(self):
        self.assertEqual(reverse_mapper('drc:document__identificatie'), 'identificatie')
        self.assertEqual(reverse_mapper('drc:document__identificatie', 'document'), 'identificatie')

    def test_mapper_get_connection(self):
        self.assertEqual(reverse_mapper('drc:connectie__zaakurl', 'connection'), 'object')

    def test_mapper_get_zaaktype(self):
        self.assertEqual(reverse_mapper('drc:zaaktype__identificatie', 'zaaktype'), 'identificatie')

    def test_mapper_get_zaak(self):
        self.assertEqual(reverse_mapper('drc:zaak__identificatie', 'zaak'), 'identificatie')

    def test_mapper_get_unknown(self):
        self.assertIsNone(reverse_mapper('drc:document__identificatie', 'unknown'))
