import base64
import logging

from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_string

from cmislib.exceptions import UpdateConflictException

# from .cache import cache
from .client import cmis_client
from .exceptions import DocumentExistsError

logger = logging.getLogger(__name__)


class CMISDRCStorageBackend(import_string(settings.ABSTRACT_BASE_CLASS)):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.

    This class is based on:
    drc.backend.abstract.BaseDRCStorageBackend
    """
    def create_document(self, validated_data, inhoud):
        identificatie = validated_data.pop('identificatie')

        try:
            cmis_doc = cmis_client.create_document(identificatie, validated_data, inhoud)
            dict_doc = self._create_dict_from_cmis_doc(cmis_doc)
            return dict_doc
        except UpdateConflictException:
            error_message = 'Document is niet uniek. Dit kan liggen aan de titel, inhoud of documentnaam'
            raise self.exception_class({None: error_message}, create=True)
        except DocumentExistsError as e:
            raise self.exception_class({None: e.message}, create=True)

    def get_documents(self):
        cmis_documents = cmis_client.get_cmis_documents()

        documents_data = []
        for cmis_doc in cmis_documents:
            dict_document = self._create_dict_from_cmis_doc(cmis_doc)
            if dict_document:
                documents_data.append(dict_document)

        return documents_data

    def update_enkelvoudiginformatieobject(self, validated_data, identificatie, inhoud):
        cmis_document = cmis_client.update_document(identificatie, validated_data, inhoud)
        return self._create_dict_from_cmis_doc(cmis_document)

    def get_document(self, uuid):
        cmis_document = cmis_client.get_cmis_document(identificatie=uuid)
        return self._create_dict_from_cmis_doc(cmis_document)

    def get_document_cases(self):
        cmis_documents = cmis_client.get_cmis_documents(filter_case=True)

        documents_data = []
        for cmis_doc in cmis_documents:
            dict_document = self._create_case_dict_from_cmis_doc(cmis_doc)
            if dict_document:
                print(dict_document)
                # documents_data.append(dict_document)

        return documents_data

    def create_case_link(self, validated_data):
        """
        There are 2 possible paths here,
        1. There is no case connected to the document yet. So the document can be connected to the case.
        2. There is a case connected to the document, so we need to create a copy of the document.
        """
        document_id = validated_data.get('informatieobject').split('/')[-1]
        cmis_doc = cmis_client.get_cmis_document(identificatie=document_id)

        if not cmis_doc.properties.get('drc:oio_zaak_url'):
            cmis_client.update_case_connection(cmis_doc, validated_data)
            folder = cmis_client.get_folder_from_case_url(validated_data.get('object'))
            if folder:
                cmis_client.move_to_case(cmis_doc, folder)
            else:
                assert False, "Should make create a cache for things todo"
        else:
            assert False, 'Has a case connected.'

    def _create_dict_from_cmis_doc(self, cmis_doc):
        properties = cmis_doc.getProperties()

        # Values that need some parsing.
        creatiedatum = properties.get("drc:creatiedatum")
        if creatiedatum:
            creatiedatum = creatiedatum.date()

        ontvangstdatum = properties.get("drc:ontvangstdatum")
        if ontvangstdatum:
            ontvangstdatum = ontvangstdatum.date()

        verzenddatum = properties.get("drc:verzenddatum")
        if verzenddatum:
            verzenddatum = verzenddatum.date()

        ondertekening_datum = properties.get("drc:ondertekening_datum")
        if ondertekening_datum:
            ondertekening_datum = ondertekening_datum.date()

        integriteit_datum = properties.get("drc:integriteit_datum")
        if integriteit_datum:
            integriteit_datum = integriteit_datum.date()

        identificatie = properties.get("drc:identificatie")

        cmis_id = properties.get("cmis:versionSeriesId").split('/')[-1]

        try:
            inhoud = base64.b64encode(cmis_doc.getContentStream().read()).decode("utf-8")
        except AssertionError:
            return None
        else:
            url = "{}{}".format(settings.HOST_URL, reverse(
                'enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
            ))
            return {
                "url": url,
                "inhoud": url,
                "creatiedatum": creatiedatum,
                "ontvangstdatum": ontvangstdatum,
                "verzenddatum": verzenddatum,
                "integriteit_datum": integriteit_datum,
                "ondertekening_datum": ondertekening_datum,
                "titel": properties.get("cmis:name"),
                "identificatie": identificatie,
                "bronorganisatie": properties.get("drc:bronorganisatie"),
                "vertrouwelijkaanduiding": properties.get("drc:vertrouwelijkaanduiding"),
                "auteur": properties.get("drc:auteur"),
                "status": properties.get("drc:status"),
                "beschrijving": properties.get("drc:beschrijving"),
                "indicatie_gebruiksrecht": properties.get("drc:indicatie_gebruiksrecht"),
                "ondertekening_soort": properties.get("drc:ondertekening_soort"),
                "informatieobjecttype": properties.get("drc:informatieobjecttype"),
                "formaat": properties.get("drc:formaat"),
                "taal": properties.get("drc:taal"),
                "bestandsnaam": properties.get("drc:bestandsnaam"),
                "link": properties.get("drc:link"),
                "integriteit_algoritme": properties.get("drc:integriteit_algoritme"),
                "integriteit_waarde": properties.get("drc:integriteit_waarde"),
                "bestandsomvang": len(inhoud),
            }

    def _create_case_dict_from_cmis_doc(self, cmis_doc):
        properties = cmis_doc.getProperties()

        # Values that need some parsing.
        creatiedatum = properties.get("drc:creatiedatum")
        if creatiedatum:
            creatiedatum = creatiedatum.date()

        ontvangstdatum = properties.get("drc:ontvangstdatum")
        if ontvangstdatum:
            ontvangstdatum = ontvangstdatum.date()

        verzenddatum = properties.get("drc:verzenddatum")
        if verzenddatum:
            verzenddatum = verzenddatum.date()

        ondertekening_datum = properties.get("drc:ondertekening_datum")
        if ondertekening_datum:
            ondertekening_datum = ondertekening_datum.date()

        integriteit_datum = properties.get("drc:integriteit_datum")
        if integriteit_datum:
            integriteit_datum = integriteit_datum.date()

        properties.get("drc:identificatie")

        cmis_id = properties.get("cmis:versionSeriesId").split('/')[-1]

        url = "{}{}".format(settings.HOST_URL, reverse(
            'objectinformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
        ))
        eio_url = "{}{}".format(settings.HOST_URL, reverse(
            'enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
        ))

        return {
            "url": url,
            "informatieobject": eio_url,
            "object": properties.get('drc:oio_zaak_url'),
            "object_type": properties.get("drc:oio_object_type"),
            "aard_relatie_weergave": properties.get("drc:oio_aard_relatie_weergave"),
            "titel": properties.get("drc:oio_titel"),
            "beschrijving": properties.get("drc:oio_beschrijving"),
            "registratiedatum": properties.get("drc:oio_registratiedatum"),
        }
