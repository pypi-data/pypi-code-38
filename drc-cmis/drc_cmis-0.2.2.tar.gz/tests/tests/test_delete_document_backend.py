from io import BytesIO

from django.test import TestCase

from tests.app.backend import BackendException

from drc_cmis import settings
from drc_cmis.backend import CMISDRCStorageBackend
from drc_cmis.client import cmis_client
from drc_cmis.models import CMISConfig, CMISFolderLocation

from .factories import EnkelvoudigInformatieObjectFactory
from .mixins import DMSMixin


class CMISDeleteDocumentTests(DMSMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.backend = CMISDRCStorageBackend()
        location = CMISFolderLocation.objects.create(location=settings.BASE_FOLDER_LOCATION)
        config = CMISConfig.get_solo()
        config.locations.add(location)

    def test_delete_document_no_document(self):
        with self.assertRaises(BackendException):
            self.backend.delete_document('identification')

    def test_delete_documents(self):
        eio = EnkelvoudigInformatieObjectFactory(identificatie='test')
        eio_dict = eio.__dict__

        cmis_doc = cmis_client.create_document(eio.identificatie, eio_dict.copy(), BytesIO(b'some content'))
        self.assertIsNotNone(cmis_doc)
        self.assertFalse(cmis_doc.properties.get('drc:document__verwijderd'))

        self.backend.delete_document('test')
        cmis_doc.reload()
        self.assertTrue(cmis_doc.properties.get('drc:document__verwijderd'))
