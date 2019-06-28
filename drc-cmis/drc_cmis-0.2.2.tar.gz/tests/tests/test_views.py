from io import BytesIO

from django.urls import reverse

from django_webtest import WebTest

from drc_cmis import settings
from drc_cmis.backend import CMISDRCStorageBackend
from drc_cmis.models import CMISConfig, CMISFolderLocation

from .factories import EnkelvoudigInformatieObjectFactory
from .mixins import DMSMixin


class CmisDownloadViewTests(DMSMixin, WebTest):
    def setUp(self):
        super().setUp()

        self.backend = CMISDRCStorageBackend()
        location = CMISFolderLocation.objects.create(location=settings.BASE_FOLDER_LOCATION)
        config = CMISConfig.get_solo()
        config.locations.add(location)

    def test_download_existing_document(self):
        eio = EnkelvoudigInformatieObjectFactory()
        document = self.backend.create_document(eio.__dict__.copy(), BytesIO(b'some content'))
        self.assertIsNotNone(document)

        response = self.app.get(document.inhoud.replace('testserver', ''))
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.content_disposition, f'attachment; filename={document.titel}.bin')  # TODO: HAve a look here
        self.assertEqual(response.content, b'some content')

    def test_download_non_existing_document(self):
        eio = EnkelvoudigInformatieObjectFactory()
        document = self.backend.create_document(eio.__dict__.copy(), BytesIO(b'some content'))
        self.assertIsNotNone(document)

        response = self.app.get(document.inhoud.replace('testserver', '').replace('.bin', 'extra.bin'), status=404)
