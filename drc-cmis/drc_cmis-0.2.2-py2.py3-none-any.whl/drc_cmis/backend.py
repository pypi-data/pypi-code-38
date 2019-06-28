import logging

from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string

from cmislib.exceptions import UpdateConflictException

from .client import cmis_client
from .client.convert import (
    create_enkelvoudiginformatieobject, create_objectinformatieobject
)
from .client.exceptions import DocumentDoesNotExistError, DocumentExistsError

logger = logging.getLogger(__name__)


class CMISDRCStorageBackend(import_string(settings.ABSTRACT_BASE_CLASS)):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.

    This class is based on:
        drc.backend.abstract.BaseDRCStorageBackend
    """

    def create_document(self, data, content):
        """
        Create a new document in the CMIS backend.

        Args:
            data (dict): A dict containing the values returned from the serializer.
            content (BytesStream): The content of the document.

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            BackendException: Raised a backend exception if the document exists.
            BackendException: Raised a backend exception if there is a document with the same name.

        """
        identification = data.pop("identificatie")

        try:
            cmis_doc = cmis_client.create_document(identification, data, content)
            dict_doc = create_enkelvoudiginformatieobject(cmis_doc, self.eio_dataclass)
            return dict_doc
        except UpdateConflictException:
            error_message = "Document is niet uniek. Dit kan liggen aan de titel, inhoud of documentnaam"
            raise self.exception_class({None: error_message}, create=True)
        except DocumentExistsError as e:
            raise self.exception_class({None: e.message}, create=True)

    def get_documents(self, filters=None):
        """
        Fetch all the documents from CMIS backend.

        Args:
            filters (dict or None): A dict with the filters that need to be applied.

        Returns:
            dataclass: A list of enkelvoudig informatieobject dataclass.

        """
        cmis_documents = cmis_client.get_cmis_documents(filters=filters)
        documents_data = []
        for cmis_doc in cmis_documents:
            dict_document = create_enkelvoudiginformatieobject(cmis_doc, self.eio_dataclass)
            documents_data.append(dict_document)

        return documents_data

    def get_document(self, identification):
        """
        Get a document by cmis identification.

        Args:
            identification (str): The cmis object id (only the uuid part).

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            BackendException: Raised a backend exception if the document does not exists.

        """

        try:
            cmis_document = cmis_client.get_cmis_document(identification)
        except DocumentDoesNotExistError as e:
            raise self.exception_class({None: e.message}, create=True)
        else:
            return create_enkelvoudiginformatieobject(cmis_document, self.eio_dataclass)

    def update_document(self, identification, data, content):
        """
        Update the document that is saved in the drc.

        Args:
            identification (str): The identification from the document.
            data (dict): A dict with the fields that need to be updated.
            content (BytesStream): The content of the document.

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            BackendException: Raised a backend exception if the document does not exists.

        """

        try:
            cmis_document = cmis_client.update_cmis_document(identification, data, content)
        except DocumentDoesNotExistError as e:
            raise self.exception_class({None: e.message}, create=True)
        else:
            return create_enkelvoudiginformatieobject(cmis_document, self.eio_dataclass)

    def delete_document(self, identification):
        """
        A request to delete the document.

        Args:
            identification (str): The identification of the document.

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            BackendException: Raised a backend exception if the document does not exists.

        """

        try:
            cmis_document = cmis_client.delete_cmis_document(identification)
        except DocumentDoesNotExistError as e:
            raise self.exception_class({None: e.message}, create=True)
        else:
            return create_enkelvoudiginformatieobject(cmis_document, self.eio_dataclass)

    def create_document_case_connection(self, data):
        """
        Create the connection between a document and a case folder.

        There are 2 possible paths here,
        1. There is no case connected to the document yet. So the document can be connected to the case.
            1.1. If there is a folder, move the document into the correct folder.
        2. There is a case connected to the document, so we need to create a copy of the document.

        Args:
            data (dict): A dict containing the values returned from the serializer.

        Returns:
            dataclass: An object informatieobject dataclass.

        """

        if not data.get("registratiedatum"):
            data["registratiedatum"] = timezone.now()

        document_id = data.get("informatieobject").split("/")[-1]
        cmis_doc = cmis_client.get_cmis_document(document_id)
        folder = cmis_client.get_folder_from_case_url(data.get("object"))

        zaak_url = cmis_doc.properties.get("drc:connectie__zaakurl")
        print('= OIO ==================================================')

        print(zaak_url)
        print(data.get("object"))
        if not zaak_url:
            print('No Case_url')
            cmis_doc = cmis_client.update_case_connection(cmis_doc, data)
            if folder:
                cmis_client.move_to_case(cmis_doc, folder)
        elif zaak_url == data.get("object"):
            print('Skip, because they are the same.')
            pass
        else:
            print('Start copying')
            cmis_client.copy_document(cmis_doc, folder, data)
        print('= END OIO ==================================================')
        objectinformatieobject = create_objectinformatieobject(cmis_doc, self.oio_dataclass)
        return objectinformatieobject

    def get_document_case_connections(self):
        """
        Get all connections between case folders and documents.

        Returns:
            dataclass: A list of object informatieobject dataclass.

        """

        cmis_documents = cmis_client.get_cmis_documents(filters={"drc:connectie__zaakurl": "NOT NULL"})
        documents_data = []
        for cmis_doc in cmis_documents:
            dict_document = create_objectinformatieobject(cmis_doc, self.oio_dataclass)
            if dict_document:
                documents_data.append(dict_document)

        return documents_data

    def get_document_case_connection(self, identification):
        """
        Get a single connection by identification.

        Args:
            identification (str): the CMIS id from the connected document.

        Returns:
            dataclass: A object informatieobject dataclass.

        Raises:
            BackendException: If the document can not be found.

        """

        try:
            cmis_document = cmis_client.get_cmis_document(
                identification, filters={"drc:connectie__zaakurl": "NOT NULL"}
            )
        except DocumentDoesNotExistError as e:
            raise self.exception_class({None: e.message}, create=True)
        else:
            objectinformatieobject = create_objectinformatieobject(cmis_document, self.oio_dataclass)
            return objectinformatieobject

    def update_document_case_connection(self, identification, data):
        """
        Update the connection.

        Args:
            identification (str): The CMIS id of the document.
            data (dict): The data that needs to be updated.

        Returns:
            dataclass: A object informatieobject dataclass.

        Raises:
            BackendException: If the document can not be found.

        """

        try:
            cmis_document = cmis_client.update_case_connection(identification, data)
        except DocumentDoesNotExistError as e:
            raise self.exception_class({None: e.message}, create=True)
        else:
            objectinformatieobject = create_objectinformatieobject(cmis_document, self.oio_dataclass)
            return objectinformatieobject

    def delete_document_case_connection(self, identification):
        """
        Uncouple a document from the case folder.

        Args:
            identification (str): The CMIS id of the document.

        Returns:
            dataclass: A object informatieobject dataclass.

        Raises:
            BackendException: If the document can not be found.

        """

        try:
            cmis_document = cmis_client.delete_case_connection(identification)
        except DocumentDoesNotExistError as e:
            raise self.exception_class({None: e.message}, create=True)
        else:
            objectinformatieobject = create_objectinformatieobject(cmis_document, self.oio_dataclass)
            return objectinformatieobject
