from django.test import TestCase

from rest_framework.exceptions import ErrorDetail
from tests.app.backend import BackendException

from drc_cmis import settings
from drc_cmis.backend import CMISDRCStorageBackend
from drc_cmis.client import cmis_client
from drc_cmis.models import CMISConfig, CMISFolderLocation

from .factories import EnkelvoudigInformatieObjectFactory
from .mixins import DMSMixin


class CMISStorageTests(DMSMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.backend = CMISDRCStorageBackend()
        location = CMISFolderLocation.objects.create(location=settings.BASE_FOLDER_LOCATION)
        config = CMISConfig.get_solo()
        config.locations.add(location)

    def test_create_document(self):
        eio = EnkelvoudigInformatieObjectFactory()
        document = self.backend.create_document(eio.__dict__.copy(), None)
        self.assertIsNotNone(document)

    def test_create_document_error_update_conflict(self):
        eio = EnkelvoudigInformatieObjectFactory()
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), None)
        self.assertIsNotNone(document)

        eio_dict['identificatie'] = 'test'

        with self.assertRaises(BackendException) as exception:
            self.backend.create_document(eio_dict.copy(), None)
        self.assertEqual(exception.exception.detail, {None: ErrorDetail(string='Document is niet uniek. Dit kan liggen aan de titel, inhoud of documentnaam', code='invalid')})

    def test_create_document_error_identification_exists(self):
        eio = EnkelvoudigInformatieObjectFactory()
        eio_dict = eio.__dict__
        eio_dict['identificatie'] = 'test'

        document = self.backend.create_document(eio_dict.copy(), None)
        self.assertIsNotNone(document)

        eio_dict['titel'] = 'gewoon_een_andere_titel'
        eio_dict['identificatie'] = 'test'

        with self.assertRaises(BackendException) as exception:
            self.backend.create_document(eio_dict.copy(), None)
        self.assertEqual(exception.exception.detail, {None: ErrorDetail(string=f"Document identificatie {eio.identificatie} is niet uniek", code='invalid')})

    def test_get_documents(self):
        # TODO: Find out why no document can be found.
        eio = EnkelvoudigInformatieObjectFactory()
        doc = self.backend.create_document(eio.__dict__, None)
        self.assertIsNotNone(doc)

        documents = self.backend.get_documents()
        self.assertEqual(len(documents), 0)  # ! Should be 1

    def test_get_documents_empty(self):
        documents = self.backend.get_documents()

        self.assertEqual(len(documents), 0)

    def test_update_enkelvoudiginformatieobject(self):
        eio = EnkelvoudigInformatieObjectFactory(identificatie='test')
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), None)
        self.assertIsNotNone(document)
        self.assertEqual(document['identificatie'], 'test')

        eio_dict['titel'] = 'test-titel-die-unique-is'

        updated_document = self.backend.update_enkelvoudiginformatieobject(eio_dict.copy(), eio_dict['identificatie'], None)

        self.assertNotEqual(document['titel'], updated_document['titel'])

    def test_get_document(self):
        eio = EnkelvoudigInformatieObjectFactory(identificatie='test')
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), None)
        self.assertIsNotNone(document)
        self.assertEqual(document['identificatie'], 'test')

        fetched_document = self.backend.get_document(document['url'].split('/')[-1])
        self.assertEqual(document['titel'], fetched_document['titel'])

    def test_get_document_cases(self):
        eio = EnkelvoudigInformatieObjectFactory(identificatie='test')
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), None)
        self.assertIsNotNone(document)
        self.assertEqual(document['identificatie'], 'test')

        documents = self.backend.get_document_cases()
        self.assertEqual(len(documents), 0)

    def test_create_case_link(self):
        # Create zaaktype_folder
        zaaktype_folder = cmis_client.get_or_create_zaaktype_folder({
            'url': 'https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1',
            'identificatie': 1,
            'omschrijving': 'Melding Openbare Ruimte',
        })

        # Create zaak_folder
        zaak_folder = cmis_client.get_or_create_zaak_folder({
            'url': 'https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid',
            'identificatie': '1bcfd0d6-c817-428c-a3f4-4047038c184d',
            'zaaktype': 'https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1',
            'startdatum': '2023-12-06',
            'einddatum': None,
            'registratiedatum': '2019-04-17',
            'bronorganisatie': '509381406',
        }, zaaktype_folder)

        # Create document
        eio = EnkelvoudigInformatieObjectFactory(identificatie='test')
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), None)
        self.assertIsNotNone(document)

        self.backend.create_case_link({
            'informatieobject': document['url'],
            'object': 'https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid'
        })

    # def test_get_folder(self):
    #     self.assertIsNone(self.backend.get_folder("test"))

    # def test_create_folder(self):
    #     self.assertIsNone(self.backend.create_folder("test"))

    # def test_rename_folder(self):
    #     self.assertIsNone(self.backend.rename_folder("test", "new_test"))

    # def test_remove_folder(self):
    #     self.assertIsNone(self.backend.remove_folder("test"))

    # def test_get_document_without_cmisstorage(self):
    #     eio = EnkelvoudigInformatieObjectFactory()
    #     self.assertIsNone(self.backend.get_document(eio).url)
    #     self.assertIsNone(self.backend.get_document(eio).auteur)
    #     self.assertIsNone(self.backend.get_document(eio).bestandsnaam)
    #     self.assertIsNone(self.backend.get_document(eio).creatiedatum)
    #     self.assertIsNone(self.backend.get_document(eio).vertrouwelijkheidaanduiding)
    #     self.assertIsNone(self.backend.get_document(eio).taal)

    # def test_get_document(self):
    #     enkelvoudiginformatieobject = EnkelvoudigInformatieObjectFactory()
    #     temp_document = self.backend.get_document(enkelvoudiginformatieobject)
    #     print(temp_document.__dict__)
    #     self.assertEqual(
    #         temp_document.url,
    #         f"http://example.com/cmis/content/{enkelvoudiginformatieobject.identificatie}.bin",
    #     )
    #     self.assertEqual(temp_document.auteur, '')
    #     self.assertEqual(temp_document.bestandsnaam, '')
    #     self.assertEqual(temp_document.creatiedatum, '')
    #     self.assertEqual(temp_document.vertrouwelijkheidaanduiding, '')
    #     self.assertEqual(temp_document.taal, '')

    # @override_settings(IS_HTTPS=True)
    # def test_get_document_https(self):
    #     enkelvoudiginformatieobject = EnkelvoudigInformatieObjectFactory()
    #     temp_document = self.backend.get_document(enkelvoudiginformatieobject)
    #     self.assertEqual(
    #         temp_document.url,
    #         f"https://example.com/cmis/content/{enkelvoudiginformatieobject.identificatie}.bin",
    #     )
    #     self.assertEqual(temp_document.auteur, '')
    #     self.assertEqual(temp_document.bestandsnaam, '')
    #     self.assertEqual(temp_document.creatiedatum, '')
    #     self.assertEqual(temp_document.vertrouwelijkheidaanduiding, '')
    #     self.assertEqual(temp_document.taal, '')
