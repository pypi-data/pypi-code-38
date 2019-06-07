# from unittest import skipIf

# from django.test import TestCase

# from faker import Faker

# from drc_cmis.client import cmis_client
# from drc_cmis.exceptions import DocumentConflictException
# from drc_cmis.storage import BinaireInhoud

# from ..factories import (
#     DRCCMISConnectionFactory, EnkelvoudigInformatieObjectFactory
# )
# from ..mixins import DMSMixin

# fake = Faker()


# class CMISClientTests(DMSMixin, TestCase):
#     def test_update_zaakdocument_only_props(self):
#         document = EnkelvoudigInformatieObjectFactory.create()

#         koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=document)
#         cmis_client.maak_zaakdocument_met_inhoud(koppeling, stream=document.inhoud)

#         # Update the document
#         new_file_name = fake.file_name()
#         document.titel = new_file_name
#         document.beschrijving = 'Andere beschrijving'
#         document.save()

#         result = self.cmis_client.update_zaakdocument(koppeling)
#         self.assertIsNone(result)

#         cmis_doc = self.cmis_client._get_cmis_doc(document)
#         cmis_doc = cmis_doc.getLatestVersion()
#         self.assertExpectedProps(
#             cmis_doc, {
#                 'cmis:contentStreamLength': document.inhoud.size,
#                 'drc:identificatie': str(document.identificatie),
#                 'cmis:versionSeriesCheckedOutId': None,
#                 'cmis:name': new_file_name,
#                 'drc:documentbeschrijving': 'Andere beschrijving',
#             }
#         )

#     def test_update_zaakdocument_content(self):
#         zaak_url = 'http://zaak.nl/locatie'
#         self.cmis_client.creeer_zaakfolder(zaak_url)
#         document = EnkelvoudigInformatieObjectFactory.create()
#         koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=document)
#         self.cmis_client.maak_zaakdocument_met_inhoud(koppeling, stream=document.inhoud)

#         new_file_name = fake.file_name()
#         inhoud = BinaireInhoud(b'leaky abstraction...', filename=new_file_name)

#         result = self.cmis_client.update_zaakdocument(koppeling, inhoud=inhoud)
#         self.assertIsNone(result)

#         filename, content = self.cmis_client.geef_inhoud(document)
#         self.assertEqual(filename, new_file_name)
#         self.assertEqual(content.read(), b'leaky abstraction...')

#         cmis_doc = self.cmis_client._get_cmis_doc(document)
#         cmis_doc = cmis_doc.getLatestVersion()
#         self.assertExpectedProps(
#             cmis_doc, {
#                 'cmis:contentStreamLength': 20,
#                 'drc:identificatie': str(document.identificatie),
#                 'cmis:versionSeriesCheckedOutId': None,
#                 'cmis:name': new_file_name,
#             }
#         )

#     def test_update_checked_out_zaakdocument(self):
#         zaak_url = 'http://zaak.nl/locatie'
#         self.cmis_client.creeer_zaakfolder(zaak_url)
#         document = EnkelvoudigInformatieObjectFactory.create()
#         koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=document)
#         self.cmis_client.maak_zaakdocument_met_inhoud(koppeling, stream=document.inhoud)
#         cmis_doc = self.cmis_client._get_cmis_doc(document)
#         cmis_doc.checkout()

#         new_file_name = fake.file_name()
#         inhoud = BinaireInhoud(b'leaky abstraction...', filename=new_file_name)

#         with self.assertRaises(DocumentConflictException):
#             self.cmis_client.update_zaakdocument(koppeling, inhoud=inhoud)

#     def test_update_checked_out_zaakdocument_with_checkout_id(self):
#         zaak_url = 'http://zaak.nl/locatie'
#         self.cmis_client.creeer_zaakfolder(zaak_url)
#         document = EnkelvoudigInformatieObjectFactory.create()
#         koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=document)
#         cmis_doc = self.cmis_client.maak_zaakdocument_met_inhoud(koppeling, stream=document.inhoud)

#         result = self.cmis_client.is_locked(document)
#         self.assertFalse(result)

#         pwc = cmis_doc.checkout()
#         pwc.reload()
#         checkout_id = pwc.properties['cmis:versionSeriesCheckedOutId']

#         # result = self.cmis_client.is_locked(document)
#         # self.assertFalse(result)

#         new_file_name = fake.file_name()
#         inhoud = BinaireInhoud(b'leaky abstraction...', filename=new_file_name)

#         result = self.cmis_client.update_zaakdocument(koppeling, checkout_id=checkout_id, inhoud=inhoud)
#         self.assertIsNone(result)

#         filename, content = self.cmis_client.geef_inhoud(document)
#         self.assertEqual(filename, new_file_name)
#         self.assertEqual(content.read(), b'leaky abstraction...')

#         # check that it's checked in again
#         new_pwc = cmis_doc.getPrivateWorkingCopy()
#         self.assertIsNone(new_pwc)

#     def test_update_checked_out_zaakdocument_with_incorrect_checkout_id(self):
#         zaak_url = 'http://zaak.nl/locatie'
#         self.cmis_client.creeer_zaakfolder(zaak_url)
#         document = EnkelvoudigInformatieObjectFactory.create()
#         koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=document)
#         self.cmis_client.maak_zaakdocument_met_inhoud(koppeling, stream=document.inhoud)
#         cmis_doc = self.cmis_client._get_cmis_doc(document)
#         cmis_doc.checkout()

#         new_file_name = fake.file_name()
#         inhoud = BinaireInhoud(b'leaky abstraction...', filename=new_file_name)

#         with self.assertRaises(DocumentConflictException):
#             self.cmis_client.update_zaakdocument(koppeling, checkout_id='definitely not right', inhoud=inhoud)
