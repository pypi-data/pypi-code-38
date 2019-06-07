# from datetime import datetime
# from io import BytesIO
# from time import time

# from django.test import TestCase

# import pytz

# from drc_cmis.exceptions import DocumentDoesNotExistError, DocumentExistsError

# from ..factories import (
#     DRCCMISConnectionFactory, EnkelvoudigInformatieObjectFactory
# )
# from ..mixins import DMSMixin


# def get_correct_date(document_date):
#     if isinstance(document_date, str):
#         return datetime.combine(
#             datetime.strptime(document_date, "%Y-%m-%d").date(), datetime.min.time()
#         ).replace(tzinfo=pytz.utc)
#     else:
#         return datetime.combine(document_date, datetime.min.time()).replace(
#             tzinfo=pytz.utc
#         )


# class CMISClientTests(DMSMixin, TestCase):
#     def test_maak_zaakdocument(self):
#         self.cmis_client.creeer_zaakfolder(self.zaak_url)
#         koppeling = DRCCMISConnectionFactory.create()

#         # cmis_doc = self.cmis_client._get_cmis_doc(document)
#         cmis_doc = self.cmis_client.maak_zaakdocument(koppeling, self.zaak_url)
#         koppeling.set_cmis_doc(cmis_doc)
#         # verify that it identifications are unique
#         with self.assertRaises(DocumentExistsError):
#             self.cmis_client.maak_zaakdocument(koppeling, self.zaak_url)

#         koppeling.refresh_from_db()
#         document = koppeling.enkelvoudiginformatieobject
#         # verify expected props
#         self.assertExpectedProps(
#             cmis_doc,
#             {
#                 "cmis:contentStreamFileName": document.titel,
#                 "cmis:contentStreamLength": 0,
#                 "cmis:contentStreamMimeType": "application/binary",
#                 "drc:dct.omschrijving": document.informatieobjecttype,
#                 "drc:identificatie": str(document.identificatie),
#                 "drc:documentauteur": document.auteur,
#                 "drc:documentbeschrijving": document.beschrijving,
#                 "drc:documentcreatiedatum": get_correct_date(document.creatiedatum),
#                 "drc:documentLink": None,
#                 "drc:documentontvangstdatum": document.ontvangstdatum,
#                 "drc:documentstatus": None,
#                 "drc:documenttaal": document.taal,
#                 "drc:documentversie": None,
#                 "drc:documentverzenddatum": None,
#                 "drc:vertrouwelijkaanduiding": document.vertrouwelijkheidaanduiding,
#             },
#         )

#         koppeling.refresh_from_db()
#         self.assertEqual(
#             koppeling.cmis_object_id,
#             cmis_doc.properties["cmis:objectId"].rsplit(";")[0],
#         )

#     def test_maak_zaakdocument_met_gevulde_inhoud(self):
#         self.cmis_client.creeer_zaakfolder(self.zaak_url)

#         koppeling = DRCCMISConnectionFactory.create()

#         cmis_doc = self.cmis_client.maak_zaakdocument_met_inhoud(
#             koppeling, self.zaak_url, stream=BytesIO(b"test")
#         )
#         koppeling.set_cmis_doc(cmis_doc)
#         document = koppeling.enkelvoudiginformatieobject
#         self.assertExpectedProps(
#             cmis_doc,
#             {
#                 "cmis:contentStreamFileName": document.titel,
#                 "cmis:contentStreamLength": 4,
#                 "cmis:contentStreamMimeType": "application/binary",
#                 "drc:dct.omschrijving": document.informatieobjecttype,
#                 "drc:identificatie": str(document.identificatie),
#                 "drc:documentauteur": document.auteur,
#                 "drc:documentbeschrijving": document.beschrijving,
#                 "drc:documentcreatiedatum": get_correct_date(document.creatiedatum),
#                 "drc:documentLink": None,
#                 "drc:documentontvangstdatum": document.ontvangstdatum,
#                 "drc:documentstatus": None,
#                 "drc:documenttaal": document.taal,
#                 "drc:documentversie": None,
#                 "drc:documentverzenddatum": None,
#                 "drc:vertrouwelijkaanduiding": document.vertrouwelijkheidaanduiding,
#             },
#         )

#         document.refresh_from_db()
#         self.assertEqual(
#             koppeling.cmis_object_id,
#             cmis_doc.properties["cmis:objectId"].rsplit(";")[0],
#         )

#     def test_maak_zaakdocument_met_sender_property(self):
#         self.cmis_client.creeer_zaakfolder(self.zaak_url)

#         from drc_cmis.models import CMISConfiguration

#         config = CMISConfiguration.get_solo()
#         config.sender_property = "drc:documentauteur"
#         config.save()
#         koppeling = DRCCMISConnectionFactory.create()

#         cmis_doc = self.cmis_client.maak_zaakdocument_met_inhoud(
#             koppeling, self.zaak_url, sender="maykin", stream=BytesIO(b"test")
#         )
#         koppeling.set_cmis_doc(cmis_doc)

#         document = koppeling.enkelvoudiginformatieobject
#         self.assertExpectedProps(
#             cmis_doc,
#             {
#                 "cmis:contentStreamFileName": document.titel,
#                 "cmis:contentStreamLength": 4,
#                 "cmis:contentStreamMimeType": "application/binary",
#                 "drc:dct.omschrijving": document.informatieobjecttype,
#                 "drc:identificatie": str(document.identificatie),
#                 "drc:documentauteur": "maykin",  # overridden by the sender
#                 "drc:documentbeschrijving": document.beschrijving,
#                 "drc:documentcreatiedatum": get_correct_date(document.creatiedatum),
#                 "drc:documentLink": None,
#                 "drc:documentontvangstdatum": document.ontvangstdatum,
#                 "drc:documentstatus": None,
#                 "drc:documenttaal": document.taal,
#                 "drc:documentversie": None,
#                 "drc:documentverzenddatum": None,
#                 "drc:vertrouwelijkaanduiding": document.vertrouwelijkheidaanduiding,
#             },
#         )

#         koppeling.refresh_from_db()
#         self.assertEqual(
#             koppeling.cmis_object_id,
#             cmis_doc.properties["cmis:objectId"].rsplit(";")[0],
#         )

#     def test_lees_document(self):
#         """
#         Ref #83: geefZaakdocumentLezen vraagt een kopie van het bestand op.

#         Van het bestand uit het DMS wordt opgevraagd: inhoud, bestandsnaam.
#         """
#         self.cmis_client.creeer_zaakfolder(self.zaak_url)
#         koppeling = DRCCMISConnectionFactory.create()
#         document = koppeling.enkelvoudiginformatieobject
#         cmis_doc = self.cmis_client.maak_zaakdocument(koppeling, self.zaak_url)
#         koppeling.set_cmis_doc(cmis_doc)

#         # empty by default
#         filename, file_obj = self.cmis_client.geef_inhoud(document)

#         self.assertEqual(filename, document.titel)
#         self.assertEqual(file_obj.read(), b"")

#         cmis_doc.setContentStream(BytesIO(b"some content"), "text/plain")

#         filename, file_obj = self.cmis_client.geef_inhoud(document)

#         self.assertEqual(filename, document.titel)
#         self.assertEqual(file_obj.read(), b"some content")

#     def test_lees_document_bestaad_niet(self):
#         """
#         Ref #83: geefZaakdocumentLezen vraagt een kopie van het bestand op.

#         Van het bestand uit het DMS wordt opgevraagd: inhoud, bestandsnaam.
#         """
#         self.cmis_client.creeer_zaakfolder(self.zaak_url)
#         document = EnkelvoudigInformatieObjectFactory.build(identificatie="123456")

#         # empty by default
#         filename, file_obj = self.cmis_client.geef_inhoud(document)

#         self.assertEqual(filename, None)
#         self.assertEqual(file_obj.read(), b"")

#     def test_voeg_zaakdocument_toe(self):
#         """
#         4.3.4.3 Interactie tussen ZS en DMS

#         Het ZS zorgt ervoor dat het document dat is aangeboden door de DSC wordt vastgelegd in het DMS.
#         Hiervoor maakt het ZS gebruik van de CMIS-services die aangeboden worden door het DMS. Hierbij
#         gelden de volgende eisen:
#         - Het document wordt gerelateerd aan de juiste Zaakfolder (Zie 5.1)
#         - Het document wordt opgeslagen als objecttype EDC (Zie 5.2)
#         - Minimaal de vereiste metadata voor een EDC wordt vastgelegd in de daarvoor gedefinieerde
#         objectproperties. In Tabel 3 is een mapping aangegeven tussen de StUF-ZKN-elementen en
#         CMIS-objectproperties.
#         """
#         koppeling = DRCCMISConnectionFactory.create()
#         self.cmis_client.maak_zaakdocument(koppeling)
#         koppeling.refresh_from_db()

#         result = self.cmis_client.zet_inhoud(
#             koppeling.enkelvoudiginformatieobject,
#             BytesIO(b"some content"),
#             content_type="text/plain",
#         )

#         self.assertIsNone(result)
#         filename, file_obj = self.cmis_client.geef_inhoud(
#             koppeling.enkelvoudiginformatieobject
#         )
#         self.assertEqual(file_obj.read(), b"some content")
#         self.assertEqual(filename, koppeling.enkelvoudiginformatieobject.titel)

#     def test_relateer_aan_zaak(self):
#         koppeling = DRCCMISConnectionFactory.create()
#         zaak_folder = self.cmis_client.creeer_zaakfolder(self.zaak_url)
#         self.cmis_client.maak_zaakdocument(koppeling)
#         koppeling.refresh_from_db()

#         result = self.cmis_client.relateer_aan_zaak(
#             koppeling.enkelvoudiginformatieobject, self.zaak_url
#         )
#         self.assertIsNone(result)

#         cmis_doc = self.cmis_client._get_cmis_doc(koppeling.enkelvoudiginformatieobject)
#         parents = [parent.id for parent in cmis_doc.getObjectParents()]
#         self.assertEqual(parents, [zaak_folder.id])

#     def test_ontkoppel_zaakdocument(self):
#         cmis_folder = self.cmis_client.creeer_zaakfolder(self.zaak_url)
#         koppeling = DRCCMISConnectionFactory.create()
#         self.cmis_client.maak_zaakdocument(koppeling, self.zaak_url)
#         result = self.cmis_client.ontkoppel_zaakdocument(
#             koppeling.enkelvoudiginformatieobject, self.zaak_url
#         )
#         self.assertIsNone(result)

#         # check that the zaakfolder is empty
#         self.assertFalse(cmis_folder.getChildren())

#     def test_verwijder_document(self):
#         zaak_folder = self.cmis_client.creeer_zaakfolder(self.zaak_url)
#         koppeling = DRCCMISConnectionFactory.create()

#         self.cmis_client.maak_zaakdocument(koppeling, self.zaak_url)
#         self.cmis_client.verwijder_document(koppeling.enkelvoudiginformatieobject)

#         with self.assertRaises(DocumentDoesNotExistError):
#             self.cmis_client._get_cmis_doc(koppeling.enkelvoudiginformatieobject)

#     def test_gooi_in_prullenbak(self):
#         koppeling = DRCCMISConnectionFactory.create()
#         trash_string = self.cmis_client.TRASH_FOLDER

#         trash_folder, _ = self.cmis_client._get_or_create_folder(trash_string)
#         current_trash_count = len(trash_folder.getChildren())

#         self.cmis_client.maak_zaakdocument(koppeling)
#         self.cmis_client.gooi_in_prullenbak(koppeling.enkelvoudiginformatieobject)
#         # check that it's gone
#         trash_folder, _ = self.cmis_client._get_or_create_folder(trash_string)
#         self.assertEqual(len(trash_folder.getChildren()), current_trash_count + 1)
