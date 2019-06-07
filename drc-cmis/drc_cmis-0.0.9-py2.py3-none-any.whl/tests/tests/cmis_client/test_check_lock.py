# from datetime import datetime
# from unittest import skipIf

# from django.test import TestCase

# import pytz
# from cmislib.exceptions import UpdateConflictException

# from drc_cmis.exceptions import DocumentConflictException
# from drc_cmis.storage import BinaireInhoud

# from ..factories import (
#     DRCCMISConnectionFactory, EnkelvoudigInformatieObjectFactory
# )
# from ..mixins import DMSMixin
# from .test_zaakdocument import get_correct_date


# class CMISClientTests(DMSMixin, TestCase):
#     def test_check_lock_status_unlocked(self):
#         self.cmis_client.creeer_zaakfolder(self.zaak_url)
#         document = EnkelvoudigInformatieObjectFactory.create()
#         koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=document)
#         self.cmis_client.maak_zaakdocument_met_inhoud(koppeling, stream=document.inhoud)

#         result = self.cmis_client.is_locked(document)
#         self.assertFalse(result)

#     def test_check_lock_status_locked(self):
#         self.cmis_client.creeer_zaakfolder(self.zaak_url)
#         document = EnkelvoudigInformatieObjectFactory.create()
#         koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=document)
#         self.cmis_client.maak_zaakdocument_met_inhoud(koppeling, stream=document.inhoud)
#         self.cmis_client.checkout(document)

#         result = self.cmis_client.is_locked(document)
#         self.assertTrue(result)

#     def test_create_lock_update_flow(self):
#         """
#         Assert that it's possible to create an empty document, lock it for
#         update and then effectively set the content thereby unlocking it.
#         """
#         self.cmis_client.creeer_zaakfolder(self.zaak_url)

#         document = EnkelvoudigInformatieObjectFactory.create()
#         koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=document)
#         self.cmis_client.maak_zaakdocument_met_inhoud(koppeling, stream=document.inhoud)
#         inhoud = BinaireInhoud(b'leaky abstraction...', filename='bestand.txt')

#         # flow
#         checkout_id, _checkout_by = self.cmis_client.checkout(document)  # lock for update
#         # TODO: Broken here. Test not possible
#         # with self.assertRaises(DocumentConflictException):
#         self.cmis_client.update_zaakdocument(koppeling, checkout_id, inhoud=inhoud)

#         filename, file_obj = self.cmis_client.geef_inhoud(document)

#         # make assertions about the results
#         self.assertEqual(filename, 'bestand.txt')
#         self.assertEqual(file_obj.read(), b'leaky abstraction...')

#         # verify expected props
#         cmis_doc = self.cmis_client._get_cmis_doc(document)
#         self.assertExpectedProps(cmis_doc, {
#             'cmis:contentStreamFileName': 'bestand.txt',
#             'cmis:contentStreamLength': 20,
#             'cmis:contentStreamMimeType': 'application/binary',  # the default if it couldn't be determined
#             # 'drc:dct.categorie': document.informatieobjecttype.informatieobjectcategorie,
#             'drc:dct.omschrijving': document.informatieobjecttype,
#             'drc:identificatie': str(document.identificatie),
#             'drc:documentauteur': document.auteur,
#             'drc:documentbeschrijving': document.beschrijving,
#             'drc:documentcreatiedatum': get_correct_date(document.creatiedatum),
#             # 'drc:documentformaat': None,
#             'drc:documentLink': None,
#             'drc:documentontvangstdatum': None,
#             'drc:documentstatus': None,
#             'drc:documenttaal': document.taal,
#             'drc:documentversie': None,
#             'drc:documentverzenddatum': None,
#             'drc:vertrouwelijkaanduiding': document.vertrouwelijkheidaanduiding
#         })

#         # the doc must be unlocked after update, easy check -> lock it
#         try:
#             cmis_doc.checkout()
#         except UpdateConflictException:
#             self.fail("Could not lock document after update, it was already/still locked")
