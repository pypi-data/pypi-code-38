from io import BytesIO

from django.test import TestCase

from rest_framework.exceptions import ErrorDetail
from tests.app.backend import BackendException

from drc_cmis import settings
from drc_cmis.backend import CMISDRCStorageBackend
from drc_cmis.models import CMISConfig, CMISFolderLocation

from .factories import EnkelvoudigInformatieObjectFactory
from .mixins import DMSMixin


class CMISCreateDocumentTests(DMSMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.backend = CMISDRCStorageBackend()
        location = CMISFolderLocation.objects.create(location=settings.BASE_FOLDER_LOCATION)
        config = CMISConfig.get_solo()
        config.locations.add(location)

    # CREATE DOCUMENT TESTS
    def test_create_document(self):
        eio = EnkelvoudigInformatieObjectFactory()
        document = self.backend.create_document(eio.__dict__.copy(), BytesIO(b'some content'))
        self.assertIsNotNone(document)

    # TODO: Change the workings
    # def test_create_document_error_update_conflict(self):
    #     eio = EnkelvoudigInformatieObjectFactory()
    #     eio_dict = eio.__dict__

    #     document = self.backend.create_document(eio_dict.copy(), BytesIO(b'some content'))
    #     self.assertIsNotNone(document)

    #     eio_dict['identificatie'] = 'test'

    #     with self.assertRaises(BackendException) as exception:
    #         self.backend.create_document(eio_dict.copy(), BytesIO(b'some content'))
    #     self.assertEqual(exception.exception.detail, {None: ErrorDetail(string='Document is niet uniek. Dit kan liggen aan de titel, inhoud of documentnaam', code='invalid')})

    def test_create_document_error_identification_exists(self):
        eio = EnkelvoudigInformatieObjectFactory()
        eio_dict = eio.__dict__
        eio_dict['identificatie'] = 'test'

        document = self.backend.create_document(eio_dict.copy(), BytesIO(b'some content'))
        self.assertIsNotNone(document)

        eio_dict['titel'] = 'gewoon_een_andere_titel'
        eio_dict['identificatie'] = 'test'

        with self.assertRaises(BackendException) as exception:
            self.backend.create_document(eio_dict.copy(), BytesIO(b'some content'))
        self.assertEqual(exception.exception.detail, {None: ErrorDetail(string=f"Document identificatie {eio.identificatie} is niet uniek", code='invalid')})
