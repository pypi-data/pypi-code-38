import codecs
import logging
from datetime import datetime
from io import BytesIO

from django.utils import timezone

from cmislib import CmisClient
from cmislib.exceptions import UpdateConflictException

from drc_cmis import settings

# from .choices import CMISObjectType
from .exceptions import DocumentConflictException, DocumentDoesNotExistError, DocumentExistsError
from .mapper import mapper, reverse_mapper
from .query import CMISQuery

# from .utils import upload_to

logger = logging.getLogger(__name__)


class CMISDRCClient:
    """
    DRC client implementation using the CMIS protocol.
    """

    all_documents_query = CMISQuery("SELECT * FROM cmis:document")
    all_drc_documents_query = CMISQuery("SELECT * FROM drc:document")
    documents_query = CMISQuery("SELECT * FROM drc:document WHERE %s")
    document_cases_query = CMISQuery("SELECT * FROM drc:document WHERE drc:connectie__zaakurl IS NOT NULL")
    document_via_identification_query = CMISQuery("SELECT * FROM drc:document WHERE drc:document__identificatie = '%s'")
    document_query = CMISQuery("SELECT * FROM cmis:document WHERE cmis:objectId = 'workspace://SpacesStore/%s;1.0'")
    find_folder_query = CMISQuery("SELECT * FROM drc:zaakfolder WHERE drc:zaak__url='%s'")

    _repo = None
    _root_folder = None
    _base_folder = None

    @property
    def _get_repo(self):
        """
        Connect to the CMIS repository
        """
        if not self._repo:
            from .models import CMISConfig

            config = CMISConfig.get_solo()
            _client = CmisClient(config.client_url, config.client_user, config.client_password)
            self._repo = _client.getDefaultRepository()
        return self._repo

    @property
    def _get_root_folder(self):
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

        TODO: create custom model.
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
    def create_document(self, identificatie, data, stream=None):
        """
        :param identificatie: EnkelvoudigInformatieObject identificatie
        :param data: De data voor de properties.
        :param stream: Inhoud van het document.

        :return: AtomPubDocument instance die aangemaakt werd.
        :raises: DocumentExistsError wanneer er al een document met dezelfde identificatie bestaat, binnen de zaakfolder
        """
        self._check_document_exists(identificatie)

        now = datetime.now()

        if stream is None:
            stream = BytesIO()

        year_folder = self._get_or_create_folder(str(now.year), self._get_base_folder)
        month_folder = self._get_or_create_folder(str(now.month), year_folder)
        day_folder = self._get_or_create_folder(str(now.day), month_folder)
        properties = self._build_properties(identificatie, data)

        return self._get_repo.createDocument(
            name=data.get("titel"), properties=properties, contentFile=stream, contentType=None, parentFolder=day_folder
        )

    def get_cmis_documents(self, filter_case=False, filters=None):
        """
        Gives a list of cmis documents.

        :return: :class:`AtomPubDocument` list
        """
        from .models import CMISConfig

        if filters:
            filter_string = ""
            for key, value in filters.items():
                if value:
                    filter_string = f"{mapper(key)} = '{value}' AND"

            if filter_string.endswith(" AND"):
                filter_string = filter_string[:-4]
            query = self.documents_query(filter_string)
        elif filter_case:
            query = self.document_cases_query()
        else:
            config = CMISConfig.get_solo()
            folders = config.locations.values_list("location", flat=True)
            folder_query = ""
            for index, folder in enumerate(folders):
                cmis_folder = self._get_or_create_folder(folder, self._get_root_folder)
                folder_query += f"IN_TREE('{cmis_folder.properties.get('cmis:objectId')}') "
                if index + 1 < len(folders):
                    folder_query += "OR "
            query = self.documents_query(folder_query)

        # Remove the /'s from the string
        query = codecs.escape_decode(query)[0].decode()
        print(query)
        result_set = self._get_repo.query(query)
        unpacked_result_set = [item for item in result_set]
        cmis_documents = [doc.getLatestVersion() for doc in unpacked_result_set]
        return cmis_documents

    def get_cmis_document(self, identificatie, document_query=None):
        """
        Given a cmis document instance.

        :param identificatie.
        :return: :class:`AtomPubDocument` object
        """
        if not document_query:
            document_query = self.document_query
        query = document_query(identificatie)
        result_set = self._get_repo.query(query)
        unpacked_result_set = [item for item in result_set]
        if not unpacked_result_set:
            error_string = "Document met identificatie {} bestaat niet in het CMIS connection".format(identificatie)
            raise DocumentDoesNotExistError(error_string)

        doc = unpacked_result_set[0]
        doc = doc.getLatestVersion()
        return doc

    def update_cmis_document(self, identificatie, data, stream=None):
        cmis_doc = self.get_cmis_document(identificatie, self.document_via_identification_query)

        # build up the properties
        current_properties = cmis_doc.properties
        new_properties = self._build_properties(identificatie, data)
        diff_properties = {key: value for key, value in new_properties.items() if current_properties.get(key) != new_properties.get(key)}

        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc

        if stream is not None:
            cmis_doc.setContentStream(stream, None)

        return cmis_doc

    def delete_cmis_document(self, identificatie):
        cmis_doc = self.get_cmis_document(identificatie, self.document_via_identification_query)
        new_properties = {mapper("verwijderd"): True}

        try:
            cmis_doc.updateProperties(new_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc
        return cmis_doc

    def update_case_connection(self, cmis_doc, data):
        current_properties = cmis_doc.properties
        new_properties = self._build_case_properties(data)
        diff_properties = {key: value for key, value in new_properties.items() if current_properties.get(key) != new_properties.get(key)}

        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc

    def move_to_case(self, cmis_doc, folder):
        parent = [parent for parent in cmis_doc.getObjectParents()][0]
        cmis_doc.move(parent, folder)

    def copy_document(self, cmis_doc, folder, data):
        properties = cmis_doc.properties
        new_properties = self._build_case_properties(data)
        properties.update(**new_properties)
        print(properties)
        # TODO: Make this an actual copy function.

        return cmis_client._repo.createDocumentFromSource(cmis_doc.getObjectId(), folder, properties)

    def get_folder_from_case_url(self, zaak_url):
        query = self.find_folder_query(zaak_url)
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
        existing = next((child for child in parent.getChildren() if str(child.name) == str(name)), None)
        if existing is not None:
            return existing
        return None

    def _build_properties(self, identificatie, data):
        base_properties = {mapper(key): value for key, value in data.items() if mapper(key)}
        base_properties["cmis:objectTypeId"] = "D:drc:document"
        base_properties[mapper("identificatie")] = identificatie
        return base_properties

    def _build_case_properties(self, data):
        return {
            mapper("object", "connection"): data.get("object"),
            mapper("objectType", "connection"): data.get("objectType"),
            mapper("aardRelatieWeergave", "connection"): data.get("aardRelatieWeergave"),
            mapper("titel", "connection"): data.get("titel"),
            mapper("beschrijving", "connection"): data.get("beschrijving"),
            mapper("registratieDatum", "connection"): timezone.now().date(),
        }

    def _check_document_exists(self, identificatie):
        try:
            self.get_cmis_document(identificatie, self.document_via_identification_query)
        except DocumentDoesNotExistError:
            pass
        else:
            error_string = "Document identificatie {} is niet uniek".format(identificatie)
            raise DocumentExistsError(error_string)


cmis_client = CMISDRCClient()
