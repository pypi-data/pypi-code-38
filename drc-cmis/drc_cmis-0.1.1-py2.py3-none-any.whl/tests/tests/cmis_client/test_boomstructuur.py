# from time import time
# from unittest import skipIf

# from django.test import TestCase

# from cmislib.exceptions import ObjectNotFoundException

# from ..mixins import DMSMixin


# class CMISClientTests(DMSMixin, TestCase):
#     def test_boomstructuur(self):
#         """
#         Test dat de boomstructuur Zaken -> Zaaktype -> Zaak gemaakt wordt.
#         """
#         with self.assertRaises(ObjectNotFoundException):
#             self.cmis_client._repo.getObjectByPath('/Zaken')

#         self.cmis_client.creeer_zaakfolder(self.zaak_url)

#         # Zaken root folder
#         root_folder = self.cmis_client._repo.getObjectByPath('/Zaken')

#         children = [child for child in root_folder.getChildren()]
#         self.assertEqual(len(children), 1)

#         # zaak subfolder
#         zaak_folder = children[0]
#         self.assertEqual(zaak_folder.name, 'httpzaaknllocatie')
#         self.assertExpectedProps(zaak_folder, {
#             'cmis:objectTypeId': 'F:drc:zaak',
#             'cmis:baseTypeId': 'cmis:folder',
#             'cmis:path': '/Zaken/httpzaaknllocatie',
#             'drc:startdatum': None,
#             'drc:einddatum': None,
#             'drc:zaakniveau': None,  # TODO
#             'drc:deelzakenindicatie': None,  # TODO
#             'drc:registratiedatum': None,
#             'drc:archiefnominatie': None,
#             'drc:datumVernietigDossier': None,
#         })

#     def test_boomstructuur_unique_name(self):
#         """
#         Test dat de boomstructuur Zaken -> Zaaktype -> Zaak gemaakt wordt.
#         """
#         with self.assertRaises(ObjectNotFoundException):
#             self.cmis_client._repo.getObjectByPath('/Zaken')

#         stamp = time()
#         self.cmis_client.creeer_zaakfolder(stamp)

#         # Zaken root folder
#         root_folder = self.cmis_client._repo.getObjectByPath('/Zaken')

#         children = [child for child in root_folder.getChildren()]
#         self.assertEqual(len(children), 1)

#         # zaak subfolder
#         zaak_folder = children[0]
#         self.assertEqual(zaak_folder.name, '{}'.format(stamp).replace('.', ''))
#         self.assertExpectedProps(zaak_folder, {
#             'cmis:objectTypeId': 'F:drc:zaak',
#             'cmis:baseTypeId': 'cmis:folder',
#             'cmis:path': '/Zaken/{}'.format(stamp).replace('.', ''),
#             'drc:startdatum': None,
#             'drc:einddatum': None,
#             'drc:zaakniveau': None,  # TODO
#             'drc:deelzakenindicatie': None,  # TODO
#             'drc:registratiedatum': None,
#             'drc:archiefnominatie': None,
#             'drc:datumVernietigDossier': None,
#         })
