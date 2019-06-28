import codecs
import logging
import random
import string
from datetime import datetime
from io import BytesIO

from cmislib import CmisClient
from cmislib.exceptions import UpdateConflictException

from drc_cmis import settings

from .exceptions import (
    DocumentConflictException, DocumentDoesNotExistError, DocumentExistsError
)
from .mapper import mapper
from .query import CMISQuery

logger = logging.getLogger(__name__)


class CMISDRCClient:
    """
    DRC client implementation using the CMIS protocol.

    This class makes it easier to query for everything you need.
    """

    documents_in_folders_query = CMISQuery("SELECT * FROM drc:document WHERE %s")
    find_folder_by_case_url_query = CMISQuery("SELECT * FROM drc:zaakfolder WHERE drc:zaak__url='%s'")

    document_via_identification_query = CMISQuery(
        "SELECT * FROM drc:document WHERE drc:document__identificatie = '%s' %s"
    )
    document_via_cmis_id_query = CMISQuery(
        "SELECT * FROM drc:document WHERE cmis:objectId = 'workspace://SpacesStore/%s;1.0' %s"
    )

    _repo = None
    _root_folder = None
    _base_folder = None

    @property
    def _get_repo(self):
        """
        Connect to the CMIS repository
        """
        if not self._repo:
            from drc_cmis.models import CMISConfig

            config = CMISConfig.get_solo()
            _client = CmisClient(config.client_url, config.client_user, config.client_password)
            self._repo = _client.getDefaultRepository()
        return self._repo

    @property
    def _get_root_folder(self):
        """
        Get the root folder of the CMIS repository

        """

        if not self._root_folder:
            self._root_folder = self._get_repo.getObjectByPath("/")
        return self._root_folder

    @property
    def _get_base_folder(self):
        if not self._base_folder:
            self._base_folder = self._get_or_create_folder(settings.BASE_FOLDER_LOCATION, self._get_root_folder)
        return self._base_folder

    # ZRC Notification client calls.
    def get_or_create_zaaktype_folder(self, zaaktype):
        """
        Create a folder with the prefix 'zaaktype-' to make a zaaktype folder

        """

        properties = {
            "cmis:objectTypeId": "F:drc:zaaktypefolder",
            mapper("url", "zaaktype"): zaaktype.get("url"),
            mapper("identificatie", "zaaktype"): zaaktype.get("identificatie"),
        }

        folder_name = f"zaaktype-{zaaktype.get('omschrijving')}-{zaaktype.get('identificatie')}"
        cmis_folder = self._get_or_create_folder(folder_name, self._get_base_folder, properties)
        return cmis_folder

    def get_or_create_zaak_folder(self, zaak, zaaktype_folder):
        """
        Create a folder with the prefix 'zaak-' to make a zaak folder

        """

        properties = {
            "cmis:objectTypeId": "F:drc:zaakfolder",
            mapper("url", "zaak"): zaak.get("url"),
            mapper("identificatie", "zaak"): zaak.get("identificatie"),
            mapper("zaaktype", "zaak"): zaak.get("zaaktype"),
            mapper("bronorganisatie", "zaak"): zaak.get("bronorganisatie"),
        }
        cmis_folder = self._get_or_create_folder(f"zaak-{zaak.get('identificatie')}", zaaktype_folder, properties)
        return cmis_folder

    # DRC client calls.
    def create_document(self, identification, data, content=None):
        """
        Create a cmis document.

        Args:
            identification (str): A unique identifier for the document.
            data (dict): A dict with all the data that needs to be saved on the document.
            content (BytesStream): The content of the document.

        Returns:
            AtomPubDocument: A cmis document.

        Raises:
            DocumentExistsError: when a document already uses the same identifier.

        """

        self._check_document_exists(identification)

        now = datetime.now()

        if content is None:
            content = BytesIO()

        year_folder = self._get_or_create_folder(str(now.year), self._get_base_folder)
        month_folder = self._get_or_create_folder(str(now.month), year_folder)
        day_folder = self._get_or_create_folder(str(now.day), month_folder)
        properties = self._build_properties(identification, data)

        return self._get_repo.createDocument(
            name=properties.get("cmis:name"),
            properties=properties,
            contentFile=content,
            contentType=None,
            parentFolder=day_folder,
        )

    def get_cmis_documents(self, filters=None):
        """
        Gives a list of cmis documents.

        Args:
            filters (dict): A dict of filters that need to be applied to the search.

        Returns:
            AtomPubDocument: A list of CMIS documents.

        """

        from drc_cmis.models import CMISConfig

        config = CMISConfig.get_solo()
        filter_string = self._build_filter(filters)
        folders = config.locations.values_list("location", flat=True)

        for index, folder in enumerate(folders):
            cmis_folder = self._get_or_create_folder(folder, self._get_root_folder)
            filter_string += f"IN_TREE('{cmis_folder.properties.get('cmis:objectId')}') "
            if index + 1 < len(folders):
                filter_string += "OR "

        query = self.documents_in_folders_query(filter_string)
        # Remove the /'s from the string
        query = codecs.escape_decode(query)[0].decode()
        print(query)
        result_set = self._get_repo.query(query)
        unpacked_result_set = [item for item in result_set]
        return [doc.getLatestVersion() for doc in unpacked_result_set]

    def get_cmis_document(self, identification, document_query=None, filters=None):
        """
        Given a cmis document instance.

        :param identification.
        :return: :class:`AtomPubDocument` object
        """
        if not document_query:
            document_query = self.document_via_cmis_id_query

        filter_string = self._build_filter(filters, filter_string="AND ", strip_end=True)
        query = document_query(identification, filter_string)
        result_set = self._get_repo.query(query)
        unpacked_result_set = [item for item in result_set]
        if not unpacked_result_set:
            error_string = "Document met identificatie {} bestaat niet in het CMIS connection".format(identification)
            raise DocumentDoesNotExistError(error_string)

        doc = unpacked_result_set[0]
        doc = doc.getLatestVersion()
        return doc

    def update_cmis_document(self, identification, data, content=None):
        cmis_doc = self.get_cmis_document(identification, self.document_via_identification_query)

        # build up the properties
        current_properties = cmis_doc.properties
        new_properties = self._build_properties(identification, data)
        diff_properties = {
            key: value
            for key, value in new_properties.items()
            if current_properties.get(key) != new_properties.get(key)
        }

        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc

        if content is not None:
            cmis_doc.setContentStream(content, None)

        return cmis_doc

    def delete_cmis_document(self, identification):
        """
        Update the property that the document is deleted.

        Arguments:
            identification (str): The identification of the document.

        Returns:
            AtomPubDocument: A CMIS document.

        Raises:
            DocumentConflictException: If the document could not be updated.
        """
        cmis_doc = self.get_cmis_document(identification, self.document_via_identification_query)
        new_properties = {mapper("verwijderd"): True}

        try:
            cmis_doc.updateProperties(new_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc
        return cmis_doc

    def update_case_connection(self, identification, data):
        cmis_doc = self.get_cmis_document(identification)

        current_properties = cmis_doc.properties
        new_properties = self._build_case_properties(data, allow_empty=False)
        diff_properties = {
            key: value
            for key, value in new_properties.items()
            if current_properties.get(key) != new_properties.get(key)
        }

        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc
        return cmis_doc

    def delete_case_connection(self, identification):
        cmis_doc = self.get_cmis_document(identification)

        connection_count = len(list(cmis_doc.getObjectParents()))
        in_zaakfolder = False

        for parent in list(cmis_doc.getObjectParents()):
            if parent.properties.get("cmis:objectTypeId") == "F:drc:zaakfolder":
                in_zaakfolder = True

        if in_zaakfolder and connection_count == 1:
            now = datetime.now()
            year_folder = self._get_or_create_folder(str(now.year), self._get_base_folder)
            month_folder = self._get_or_create_folder(str(now.month), year_folder)
            day_folder = self._get_or_create_folder(str(now.day), month_folder)

            self.move_to_case(cmis_doc, day_folder)

        # Clear properties
        current_properties = cmis_doc.properties
        new_properties = self._build_case_properties({})
        diff_properties = {
            key: value
            for key, value in new_properties.items()
            if current_properties.get(key) != new_properties.get(key)
        }

        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc
        return cmis_doc

    def move_to_case(self, cmis_doc, folder):
        parent = [parent for parent in cmis_doc.getObjectParents()][0]
        cmis_doc.move(parent, folder)

    def copy_document(self, cmis_doc, folder, data):
        """
        We will no longer copy documents. We will create a list of extra data to the documents.
        """
        properties = {}

        properties.update(**{
            'cmis:objectTypeId': cmis_doc.properties.get('cmis:objectTypeId'),
            'drc:document__auteur': cmis_doc.properties.get('drc:document__auteur'),
            'drc:document__beschrijving': cmis_doc.properties.get('drc:document__beschrijving'),
            'drc:document__bestandsnaam': cmis_doc.properties.get('drc:document__bestandsnaam'),
            'drc:document__bronorganisatie': cmis_doc.properties.get('drc:document__bronorganisatie'),
            'drc:document__creatiedatum': cmis_doc.properties.get('drc:document__creatiedatum'),
            'drc:document__formaat': cmis_doc.properties.get('drc:document__formaat'),
            'drc:document__identificatie': cmis_doc.properties.get('drc:document__identificatie'),
            'drc:document__indicatiegebruiksrecht': cmis_doc.properties.get('drc:document__indicatiegebruiksrecht'),
            'drc:document__informatieobjecttype': cmis_doc.properties.get('drc:document__informatieobjecttype'),
            'drc:document__integriteitalgoritme': cmis_doc.properties.get('drc:document__integriteitalgoritme'),
            'drc:document__integriteitdatum': cmis_doc.properties.get('drc:document__integriteitdatum'),
            'drc:document__integriteitwaarde': cmis_doc.properties.get('drc:document__integriteitwaarde'),
            'drc:document__link': cmis_doc.properties.get('drc:document__link'),
            'drc:document__ondertekeningdatum': cmis_doc.properties.get('drc:document__ondertekeningdatum'),
            'drc:document__ondertekeningsoort': cmis_doc.properties.get('drc:document__ondertekeningsoort'),
            'drc:document__ontvangstdatum': cmis_doc.properties.get('drc:document__ontvangstdatum'),
            'drc:document__status': cmis_doc.properties.get('drc:document__status'),
            'drc:document__taal': cmis_doc.properties.get('drc:document__taal'),
            'drc:document__titel': cmis_doc.properties.get('drc:document__titel'),
            'drc:document__vertrouwelijkaanduiding': cmis_doc.properties.get('drc:document__vertrouwelijkaanduiding'),
            'drc:document__verwijderd': cmis_doc.properties.get('drc:document__verwijderd'),
            'drc:document__verzenddatum': cmis_doc.properties.get('drc:document__verzenddatum'),
        })

        new_properties = self._build_case_properties(data)
        properties.update(**new_properties)

        if not folder:
            now = datetime.now()
            year_folder = self._get_or_create_folder(str(now.year), self._get_base_folder)
            month_folder = self._get_or_create_folder(str(now.month), year_folder)
            folder = self._get_or_create_folder(str(now.day), month_folder)

        # Update the cmis:name to make it more unique
        file_name = f"{cmis_doc.properties.get(mapper('titel'))}-{self.get_random_string()}"
        properties['cmis:name'] = file_name

        # TODO: Make this an actual copy function.
        return cmis_client._repo.createDocument(
            name=file_name,
            properties=properties,
            contentFile=cmis_doc.getContentStream(),
            contentType=None,
            parentFolder=folder,
        )

    def get_random_string(self, number=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=number))

    def get_folder_from_case_url(self, zaak_url):
        query = self.find_folder_by_case_url_query(zaak_url)
        result_set = self._get_repo.query(query)
        unpacked_result_set = [item for item in result_set.getResults()]
        if unpacked_result_set:
            folder = unpacked_result_set[0]
            # ! A reload is done because there are some important values missing from the objects.
            folder.reload()
            return folder
        return None

    # Private functions.
    # TODO: Paste private functions.
    def _get_or_create_folder(self, name, parent, properties=None):
        """
        Get or create the folder with :param:`name` in :param:`parent`.

        :param name: string, the name of the folder to create.
        :param parent: parent folder to create the folder in as subfolder.
        :param properties: dictionary with cmis and/or custom properties to
          pass to the folder object
        :return: the folder that was retrieved or created.
        """
        existing = self._get_folder(name, parent)
        if existing:
            return existing
        return parent.createFolder(name, properties=properties or {})

    def _get_folder(self, name, parent):
        print(parent.getChildren())
        existing = next((child for child in parent.getChildren() if str(child.name) == str(name)), None)
        if existing is not None:
            return existing
        return None

    def _build_filter(self, filters, filter_string="", strip_end=False):
        if filters:
            for key, value in filters.items():
                if mapper(key):
                    key = mapper(key)

                if value and value in ["NULL", "NOT NULL"]:
                    filter_string += f"{key} IS {value} AND "
                elif value:
                    filter_string += f"{key} = '{value}' AND "

        if strip_end and filter_string[-4:] == "AND ":
            filter_string = filter_string[:-4]

        return filter_string

    def _build_properties(self, identification, data):
        base_properties = {mapper(key): value for key, value in data.items() if mapper(key)}
        base_properties["cmis:objectTypeId"] = "D:drc:document"
        base_properties['cmis:name'] = f"{data.get('titel')}-{self.get_random_string()}"
        base_properties[mapper("identificatie")] = identification
        return base_properties

    def _build_case_properties(self, data, allow_empty=True):
        props = {}
        if data.get("object") or allow_empty:
            props[mapper("object", "connection")] = data.get("object")
        if data.get("object_type") or allow_empty:
            props[mapper("object_type", "connection")] = data.get("object_type")
        if data.get("aard_relatie") or allow_empty:
            props[mapper("aard_relatie", "connection")] = data.get("aard_relatie")
        if data.get("titel") or allow_empty:
            props[mapper("titel", "connection")] = data.get("titel")
        if data.get("beschrijving") or allow_empty:
            props[mapper("beschrijving", "connection")] = data.get("beschrijving")
        if data.get("registratiedatum") or allow_empty:
            props[mapper("registratiedatum", "connection")] = data.get("registratiedatum")

        return props

    def _check_document_exists(self, identification):
        try:
            self.get_cmis_document(identification, self.document_via_identification_query)
        except DocumentDoesNotExistError:
            pass
        else:
            error_string = "Document identificatie {} is niet uniek".format(identification)
            raise DocumentExistsError(error_string)


cmis_client = CMISDRCClient()
