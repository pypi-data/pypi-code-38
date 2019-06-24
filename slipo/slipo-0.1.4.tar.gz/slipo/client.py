"""
SLIPO API entry point.

This class provides access to all SLIPO API functionality for accessing the user 
file system, querying the catalog, querying existing workflows and executing SLIPO 
Toolkit operations.
"""
import warnings
import requests

from typing import Union

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from .exceptions import SlipoException

from .filesystem import FileSystemClient
from .catalog import CatalogClient
from .process import ProcessClient
from .operation import OperationClient, EnumDataFormat
from .utils import json_response
from .types import InputType

# Default API endpoint
BASE_URL = 'https://app.dev.slipo.eu/'

API_VERSION = 'v1'

API_VALIDATE = 'api/{api_version}/key/validate/'


class Client(object):
    """Class implementing all SLIPO API functionality

    Args:
        api_key (str): SLIPO API key. An application key can be generated using
            the SLIPO Workbench application.
        base_url (str, optional): Base URL for SLIPO API endpoints. The default
            value is ``https://app.dev.slipo.eu/``.
        requires_ssl (bool, optional): If `False`, unsecured connections are allowed (default `True`).

    Returns:
        A :py:class:`Client <slipo.client.Client>` object.

    """

    def __init__(self,  api_key, base_url=None, requires_ssl=True):
        self.api_key = api_key
        self.base_url = self._check_base_url(base_url, requires_ssl)

        self.file_client = FileSystemClient(self.base_url, api_key)
        self.catalog_client = CatalogClient(self.base_url, api_key)
        self.process_client = ProcessClient(self.base_url, api_key)
        self.operation_client = OperationClient(self.base_url, api_key)

    def _check_base_url(self, base_url, requires_ssl):
        if not base_url:
            base_url = BASE_URL

        if not base_url.startswith("https"):
            if requires_ssl == False:
                warnings.warn('You are using an API key over an unsecured '
                              'connection!!!')
            else:
                raise SlipoException('HTTPS should be used for API requests')

            # Append a trailing / if not one exists
        if not base_url.endswith('/'):
            base_url += '/'

        return base_url

    @json_response
    def validate(self) -> None:
        """Validate current application key

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_VALIDATE.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        return requests.get(url, headers={
            'X-API-Key': self.api_key
        })       

    def file_browse(self):
        """Browse all files and folders on the remote file system.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.file_client.browse()

    def file_download(self, source: str, target: str, overwrite: bool = False) -> None:
        """Download a file from the remote file system.

        Args:
            source (str): Relative file path on the remote file system.
            target (str): The path where to save the file.
            overwrite (bool, optional): Set true if the operation should
                overwrite any existing file.

        Raises:
            SlipoException: If a network, server error or I/O error has occurred.
        """

        return self.file_client.download(source, target, overwrite=overwrite)

    def file_upload(self, source: str, target: str, overwrite: bool = False) -> None:
        """Upload a file to the remote file system.

        Note:
            File size constraints are enforced on the uploaded file. The default
            installation allows files up to 20 Mb. 

            Moreover, space quotas are applied on the server. The default user
            space is 5GB.

            Directory nesting constraints are applied for the ``target`` value. The
            default installation allows nesting of directories up to 5 levels.

        Args:
            source (str): The path of the file to upload.
            target (str): Relative path on the remote file system where to save the
                file. If the directory does not exist, it will be created.
            overwrite (bool, optional): Set true if the operation should overwrite
                any existing file.

        Raises:
            SlipoException: If a network, server error or I/O error has occurred.
        """

        # Remove leading slash character from target
        target = target[1::] if target.startswith('/') else target

        self.file_client.upload(source, target, overwrite=overwrite)

    def catalog_query(self, term: str = None, pageIndex: int = 0, pageSize: int = 10):
        """Query resource catalog for RDF datasets.

        Args:
            term (str, optional): A term for filtering resources. If specified, 
                only the resources whose name contains the term are returned.
            pageIndex (str, optional): Page index for data pagination.
            pageSize (str, optional): Page size for data pagination.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.catalog_client.query(term=term, pageIndex=pageIndex, pageSize=pageSize)

    def catalog_download(self, resource_id: int, resource_version: int, target: str):
        """Download resource to the local file system

        Args:
            resource_id (int): The resource id.
            resource_version (int): The resource revision.
            target (str): The path where to save the file.

        Raises:
            SlipoException: If a network, server error or I/O error has occurred.
        """

        return self.catalog_client.download(resource_id, resource_version, target)

    def process_query(self, term: str = None, pageIndex: int = 0, pageSize: int = 10):
        """Query workflow instances.

        Args:
            term (str, optional): A term for filtering workflows. If specified, 
                only the workflows whose name contains the term are returned.
            pageIndex (str, optional): Page index for data pagination.
            pageSize (str, optional): Page size for data pagination.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.process_client.query(term=term, pageIndex=pageIndex, pageSize=pageSize)

    def process_start(self, process_id: int, process_version: int) -> None:
        """Start or resume execution of a workflow instance.

        Args:
            process_id (int): The process id.
            process_version (int): The process revision.

        Raises:
            SlipoException: If a network or server error has occurred.
        """
        return self.process_client.start(process_id, process_version)

    def process_stop(self, process_id: int, process_version: int) -> None:
        """Stop a running workflow execution instance.

        Args:
            process_id (int): The process id.
            process_version (int): The process revision.

        Raises:
            SlipoException: If a network or server error has occurred.
        """
        return self.process_client.stop(process_id, process_version)

    def process_status(self, process_id: int, process_version: int):
        """Check the status of a workflow execution instance.

        Args:
            process_id (int): The process id.
            process_version (int): The process revision.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """
        return self.process_client.status(process_id, process_version)

    def process_file_download(self, process_id: int, process_version: int, file_id: int, target: str):
        """Download an input or output file for a specific workflow execution instance.

        During the execution of a workflow the following file types may be created:
            - ``CONFIGURATION``: Tool configuration
            - ``INPUT``: Input file
            - ``OUTPUT``: Output file
            - ``SAMPLE``: Sample data collected during step execution
            - ``KPI``: Tool specific or aggregated KPI data
            - ``QA``: Tool specific QA data
            - ``LOG``: Logs recorded during step execution 

        Args:
            process_id (int): The process id.
            process_version (int): The process revision.
            file_id (int): The file id.
            target (str): The path where to save the file.

        Raises:
            SlipoException: If a network, server error or I/O error has occurred.
        """

        return self.process_client.download(process_id, process_version, file_id, target)

    def profiles(self):
        """Browse all SLIPO Toolkit components profiles.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.operation_client.profiles()

    def transform_csv(
        self,
        path: str,
        **kwargs
    ):
        """Transforms a CSV file to a RDF dataset.

        Args:
            path (str): The relative path for a file on the remote user file
                system.
            **kwargs: Keyword arguments to control the transform operation. Options are:

                - **attrCategory** (str, optional): Field name containing literals regarding
                  classification into categories (e.g., type of points, road classes etc.)
                  for each feature.
                - **attrGeometry** (str, optional): Parameter that specifies the name of the
                  geometry column in the input dataset.
                - **attrKey** (str, optional): Field name containing unique identifier for each
                  entity (e.g., each record in the shapefile).
                - **attrName** (str, optional): Field name containing name literals
                  (i.e., strings).
                - **attrX** (str, optional): Specify attribute holding X-coordinates of
                  point locations. If inputFormat is not `CSV`, the parameter is ignored.
                - **attrY** (str, optional): Specify attribute holding Y-coordinates of
                  point locations. If inputFormat is not `CSV`, the parameter is ignored.
                - **classificationSpec** (str, optional): The relative path to a YML/CSV
                  file describing a classification scheme.
                - **defaultLang** (str, optional): Default lang for the labels created
                  in the output RDF (default: `en`).
                - delimiter (str, optional): Specify the character delimiting attribute
                  values.
                - **encoding** (str, optional): The encoding (character set) for strings in the
                  input data (default: `UTF-8`)
                - **featureSource** (str, optional): Specifies the data source provider of the
                  input features.
                - **mappingSpec** (str, optional): The relative path to a YML file containing
                  mappings from input schema to RDF according to a custom ontology.
                - **profile** (str, optional): The name of the profile to use. Profile names can
                  be retrieved using :meth:`profiles` method. If profile is not set, the
                  `mappingSpec` parameter must be set.
                - **quote** (str, optional): Specify quote character for string values.
                - **sourceCRS** (str, optional): Specify the EPSG code for the
                  source CRS (default: `EPSG:4326`).
                - **targetCRS** (str, optional): Specify the EPSG code for the
                  target CRS (default: `EPSG:4326`).

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.operation_client.transform_csv(
            path,
            **kwargs
        )

    def transform_shapefile(
        self,
        path: str,
        **kwargs
    ):
        """Transforms a SHAPEFILE file to a RDF dataset.

        Args:
            path (str): The relative path for a file on the remote user file
                system.
            **kwargs: Keyword arguments to control the transform operation. Options
                are:

                - **attrCategory** (str, optional): Field name containing literals regarding
                  classification into categories (e.g., type of points, road classes etc.)
                  for each feature.
                - **attrGeometry** (str, optional): Parameter that specifies the name of the
                  geometry column in the input dataset.
                - **attrKey** (str, optional): Field name containing unique identifier for each
                  entity (e.g., each record in the shapefile).
                - **attrName** (str, optional): Field name containing name literals
                  (i.e., strings).
                - **classificationSpec** (str, optional): The relative path to a YML/CSV
                  file describing a classification scheme.
                - **defaultLang** (str, optional): Default lang for the labels created
                  in the output RDF (default: `en`).
                - **encoding** (str, optional): The encoding (character set) for strings in the
                  input data (default: `UTF-8`)
                - **featureSource** (str, optional): Specifies the data source provider of the
                  input features.
                - **mappingSpec** (str, optional): The relative path to a YML file containing
                  mappings from input schema to RDF according to a custom ontology.
                - **profile** (str, optional): The name of the profile to use. Profile names can
                  be retrieved using :meth:`profiles` method. If profile is not set, the
                  `mappingSpec` parameter must be set.
                - **sourceCRS** (str, optional): Specify the EPSG code for the
                  source CRS (default: `EPSG:4326`).
                - **targetCRS** (str, optional): Specify the EPSG code for the
                  target CRS (default: `EPSG:4326`).

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.operation_client.transform_shapefile(
            path,
            **kwargs
        )

    def interlink(
        self,
        profile: str,
        left: InputType,
        right: InputType
    ):
        """Generates links for two RDF datasets.

        Arguments `left`, `right` and `links` may be either:

          - A :obj:`str` that represents a relative path to the remote user file system
          - A :obj:`tuple` of two integer values that represents the id and revision
            of a catalog resource.
          - A :obj:`tuple` of three integer values that represents the process id,
            process revision and output file id for a specific workflow or SLIPO API
            operation execution.

        Args:
            profile (str): The name of the profile to use. Profile names can
                be retrieved using :meth:`profiles` method.
            left (Union[str, Tuple[int, int], Tuple[int, int, int]): The `left` RDF dataset.
            right (Union[str, Tuple[int, int], Tuple[int, int, int]): The `right` RDF dataset.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.operation_client.interlink(profile, left, right)

    def fuse(
        self,
        profile: str,
        left: InputType,
        right: InputType,
        links: InputType
    ):
        """Fuses two RDF datasets using Linked Data and returns a new RDF dataset.

        Args:
            profile (str): The name of the profile to use. Profile names can
                be retrieved using :meth:`profiles` method.
            left (Union[str, Tuple[int, int], Tuple[int, int, int]): The `left` RDF dataset.
            right (Union[str, Tuple[int, int], Tuple[int, int, int]): The `right` RDF dataset.
            links (Union[str, Tuple[int, int], Tuple[int, int, int]): The links for the `left` and `right` datasets.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.operation_client.fuse(profile, left, right, links)

    def enrich(
        self,
        profile: str,
        source: InputType
    ):
        """Enriches a RDF dataset.

        Args:
            profile (str): The name of the profile to use. Profile names can
                be retrieved using :meth:`profiles` method.
            source (Union[str, Tuple[int, int], Tuple[int, int, int]): The RDF dataset to enrich.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.operation_client.enrich(profile, source)

    def export_csv(
        self,
        profile: str,
        source: InputType,
        **kwargs
    ) -> dict:
        """Exports a RDF dataset to a CSV file.

        Args:
            profile (str): The name of the profile to use. Profile names can
                be retrieved using :meth:`profiles` method.
            source (Union[str, Tuple[int, int], Tuple[int, int, int]): The RDF dataset
                to export.
            **kwargs: Keyword arguments to control the transform operation. Options are:

                - **defaultLang** (str, optional): The default language for labels created
                  in output RDF. The default is "en".
                - delimiter (str, optional):A field delimiter for records (default: `;`).
                - **encoding** (str, optional): The encoding (character set) for strings in the
                  input data (default: `UTF-8`)
                - **quote** (str, optional): Specify quote character for string values (default `"`).
                - **sourceCRS** (str, optional): Specify the EPSG code for the
                  source CRS (default: `EPSG:4326`).
                - **sparqlFile** (str, optional): The relative path to a file containing a 
                  user-specified SELECT query (in SPARQL) that will retrieve results from
                  the input RDF triples. This query should conform with the underlying ontology
                  of the input RDF triples.
                - **targetCRS** (str, optional): Specify the EPSG code for the
                  target CRS (default: `EPSG:4326`).

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.operation_client.export_csv(
            profile,
            source,
            **kwargs
        )

    def export_shapefile(
        self,
        source: InputType,
        profile: str,
        **kwargs
    ) -> dict:
        """Exports a RDF dataset to a SHAPEFILE file.

        Args:
            profile (str): The name of the profile to use. Profile names can
                be retrieved using :meth:`profiles` method.
            source (Union[str, Tuple[int, int], Tuple[int, int, int]): The RDF dataset
                to export.
            **kwargs: Keyword arguments to control the transform operation. Options
                are:

                - **defaultLang** (str, optional): The default language for labels created
                  in output RDF. The default is "en".
                - delimiter (str, optional):A field delimiter for records (default: `;`).
                - **encoding** (str, optional): The encoding (character set) for strings in the
                  input data (default: `UTF-8`)
                - **quote** (str, optional): Specify quote character for string values (default `"`).
                - **sourceCRS** (str, optional): Specify the EPSG code for the
                  source CRS (default: `EPSG:4326`).
                - **sparqlFile** (str, optional): The relative path to a file containing a 
                  user-specified SELECT query (in SPARQL) that will retrieve results from
                  the input RDF triples. This query should conform with the underlying ontology
                  of the input RDF triples.
                - **targetCRS** (str, optional): Specify the EPSG code for the
                  target CRS (default: `EPSG:4326`).

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        return self.operation_client.export_shapefile(
            profile,
            source,
            **kwargs
        )
