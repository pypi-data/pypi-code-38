import os

from django.conf import settings
from django.test import TestCase

import responses
from vng_api_common.models import APICredential

from drc_cmis.client import cmis_client
from drc_cmis.notifications import default

from .mixins import DMSMixin


class NotificationTests(DMSMixin, TestCase):
    def test_notifications_empty_dict(self):
        with self.assertRaises(KeyError):
            default.handle({})

    def test_notifications_default(self):
        default.handle({"kanaal": "random"})

    def test_notifications(self):
        default.handle({"kanaal": "zaken"})

    @responses.activate
    def test_notifications_fully_filled(self):
        with open(os.path.join(settings.PROJECT_ROOT, 'responses', 'ztc-openapi.yaml'), 'rb') as resp_file:
            responses.add(responses.GET, 'https://ref.tst.vng.cloud/ztc/api/v1/schema/openapi.yaml?v=3', body=resp_file.read(), status=200)
        with open(os.path.join(settings.PROJECT_ROOT, 'responses', 'ztc-zaaktype.json'), 'rb') as resp_file:
            responses.add(responses.GET, 'https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1', body=resp_file.read(), status=200)
        with open(os.path.join(settings.PROJECT_ROOT, 'responses', 'zrc-openapi.yaml'), 'rb') as resp_file:
            responses.add(responses.GET, 'https://ref.tst.vng.cloud/zrc/api/v1/zaken/schema/openapi.yaml?v=3', body=resp_file.read(), status=200)
        with open(os.path.join(settings.PROJECT_ROOT, 'responses', 'zrc-zaak.json'), 'rb') as resp_file:
            responses.add(responses.GET, 'https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid', body=resp_file.read(), status=200)

        APICredential.objects.create(api_root="https://ref.tst.vng.cloud/zrc/", label="ZRC", client_id="test", secret="test")
        APICredential.objects.create(api_root="https://ref.tst.vng.cloud/ztc/", label="ZTC", client_id="test", secret="test")

        data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
            "actie": "create",
            "resource": "zaak",
            "resource_url": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
                "vertrouwelijkeidaanduiding": "openbaar",
            },
        }

        default.handle(data)

        case_folder = cmis_client.get_folder_from_case_url("https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid")
        self.assertIsNotNone(case_folder)

    @responses.activate
    def test_notifications_no_resource_url(self):
        data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
            "actie": "create",
            "resource": "zaak",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
                "vertrouwelijkeidaanduiding": "openbaar",
            },
        }

        default.handle(data)

        case_folder = cmis_client.get_folder_from_case_url("https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid")
        self.assertIsNone(case_folder)

    @responses.activate
    def test_notifications_no_zaaktype(self):
        data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
            "actie": "create",
            "resource": "zaak",
            "resource_url": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "vertrouwelijkeidaanduiding": "openbaar",
            },
        }

        default.handle(data)

        case_folder = cmis_client.get_folder_from_case_url("https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid")
        self.assertIsNone(case_folder)

    @responses.activate
    def test_notifications_no_kenmerken(self):
        data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
            "actie": "create",
            "resource": "zaak",
            "resource_url": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
        }

        default.handle(data)

        case_folder = cmis_client.get_folder_from_case_url("https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid")
        self.assertIsNone(case_folder)
