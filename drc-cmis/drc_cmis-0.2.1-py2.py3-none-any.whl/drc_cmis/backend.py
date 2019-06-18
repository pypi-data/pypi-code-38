import logging

from django.conf import settings
from django.utils.module_loading import import_string

from cmislib.exceptions import UpdateConflictException

from .client import cmis_client
from .convert import create_case_dict_from_cmis_doc, create_dataclass_from_cmis_doc
from .exceptions import DocumentExistsError

logger = logging.getLogger(__name__)


class CMISDRCStorageBackend(import_string(settings.ABSTRACT_BASE_CLASS)):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.

    This class is based on:
    drc.backend.abstract.BaseDRCStorageBackend
    """

    # DOCUMENTS ====================================================================================
    # CREATE
    def create_document(self, validated_data, inhoud):
        identificatie = validated_data.pop("identificatie")

        try:
            cmis_doc = cmis_client.create_document(identificatie, validated_data, inhoud)
            dict_doc = create_dataclass_from_cmis_doc(cmis_doc, self.dataclass)
            return dict_doc
        except UpdateConflictException:
            error_message = "Document is niet uniek. Dit kan liggen aan de titel, inhoud of documentnaam"
            raise self.exception_class({None: error_message}, create=True)
        except DocumentExistsError as e:
            raise self.exception_class({None: e.message}, create=True)

    # READ
    def get_documents(self, filters=None):
        """
        Fetch all the documents from CMIS and create a dict that is compatible with the serializer.
        """
        cmis_documents = cmis_client.get_cmis_documents(filters=filters)
        documents_data = []
        for cmis_doc in cmis_documents:
            dict_document = create_dataclass_from_cmis_doc(cmis_doc, self.dataclass)
            if dict_document:
                documents_data.append(dict_document)

        return documents_data

    def get_document(self, uuid):
        cmis_document = cmis_client.get_cmis_document(identificatie=uuid)
        return create_dataclass_from_cmis_doc(cmis_document, self.dataclass)

    # UPDATE
    def update_document(self, validated_data, identificatie, inhoud):
        cmis_document = cmis_client.update_cmis_document(identificatie, validated_data, inhoud)
        return create_dataclass_from_cmis_doc(cmis_document, self.dataclass)

    # DELETE
    def delete_document(self, uuid):
        cmis_document = cmis_client.delete_cmis_document(identificatie=uuid)
        return create_dataclass_from_cmis_doc(cmis_document, self.dataclass)

    # CONNECTIONS ==================================================================================
    # CREATE
    def create_case_link(self, validated_data):
        """
        There are 2 possible paths here,
        1. There is no case connected to the document yet. So the document can be connected to the case.
        2. There is a case connected to the document, so we need to create a copy of the document.
        """
        document_id = validated_data.get("informatieobject").split("/")[-1]
        cmis_doc = cmis_client.get_cmis_document(identificatie=document_id)
        folder = cmis_client.get_folder_from_case_url(validated_data.get("object"))

        if not cmis_doc.properties.get("drc:connectie__zaakurl"):
            cmis_client.update_case_connection(cmis_doc, validated_data)
            if folder:
                cmis_client.move_to_case(cmis_doc, folder)
            else:
                return
        else:
            cmis_client.copy_document(cmis_doc, folder, validated_data)

    # READ
    def get_document_cases(self):
        """
        Get all documents that have a case url.
        """
        cmis_documents = cmis_client.get_cmis_documents(filter_case=True)
        documents_data = []
        for cmis_doc in cmis_documents:
            dict_document = create_case_dict_from_cmis_doc(cmis_doc)
            if dict_document:
                documents_data.append(dict_document)

        return documents_data

    # UPDATE
    # TODO

    # DELETE
    # TODO
