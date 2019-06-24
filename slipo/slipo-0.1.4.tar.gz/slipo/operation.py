"""
Client for executing SLIPO Toolkit component operations
"""

import json
import http
import requests

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from enum import Enum
from typing import Union, Tuple

from .exceptions import SlipoException
from .utils import json_response, file_response
from .types import InputType

API_VERSION = "v1"

API_PROFILES = '/api/{api_version}/toolkit/profiles'
API_TRANSFORM = '/api/{api_version}/toolkit/transform'
API_INTERLINK = '/api/{api_version}/toolkit/interlink'
API_FUSE = '/api/{api_version}/toolkit/fuse'
API_ENRICH = '/api/{api_version}/toolkit/enrich'
API_EXPORT = '/api/{api_version}/toolkit/export'


class EnumDataFormat(Enum):
    """
    Supported data formats for transform operations
    """

    CSV = 'CSV'
    GPX = 'GPX'
    GEOJSON = 'GEOJSON'
    JSON = 'JSON'
    OSM_PBF = 'OSM_PBF'
    OSM_XML = 'OSM_XML'
    SHAPEFILE = 'SHAPEFILE'
    RDF_XML = 'RDF_XML'
    RDF_XML_ABBREV = 'RDF_XML_ABBREV'
    TURTLE = 'TURTLE'
    XML = 'XML'
    N_TRIPLES = 'N_TRIPLES'
    N3 = 'N3'


class EnumInputType(Enum):
    """
    Supported input types for SLIPO Toolkit components operations
    """

    FILESYSTEM = 'FILESYSTEM'
    CATALOG = 'CATALOG'
    OUTPUT = 'OUTPUT'


class OperationClient(object):
    """OperationClient provides methods for executing SLIPO Toolkit components operations.

    Details about the API responses are available at the `SLIPO`_ site.

    Args:
        base_url (str): Base URL for SLIPO API endpoints. The default
            value is ``https://app.dev.slipo.eu/``.
        api_key (str): SLIPO API key. An application key can be generated using
            the SLIPO Workbench application.

    Returns:
        A :py:class:`OperationClient <slipo.operation.OperationClient>` object.

    .. _SLIPO:
       https://app.dev.slipo.eu/docs/webapp-api/index.html#api-Toolkit
    """

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

        self.headers = {
            'X-API-Key': api_key,
            'Content-type': 'application/json',
        }

    @json_response
    def profiles(self) -> dict:
        """Browse all SLIPO Toolkit components profiles.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_PROFILES.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        return requests.get(url, headers=self.headers)

    @json_response
    def _transform(
        self,
        path: str,
        inputFormat: EnumDataFormat,
        attrCategory: str = None,
        attrGeometry: str = None,
        attrKey: str = None,
        attrName: str = None,
        attrX: str = None,
        attrY: str = None,
        classificationSpec: str = None,
        defaultLang: str = 'en',
        delimiter: str = None,
        encoding: str = 'UTF-8',
        featureSource: str = None,
        mappingSpec: str = None,
        profile: str = None,
        quote: str = None,
        sourceCRS: str = 'EPSG:4326',
        targetCRS: str = 'EPSG:4326',
    ) -> dict:
        endpoint = API_TRANSFORM.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        data = {
            'path': path,
            'configuration': {
                'attrCategory': attrCategory,
                'attrGeometry': attrGeometry,
                'attrKey': attrKey,
                'attrName': attrName,
                'attrX': attrX,
                'attrY': attrY,
                'classificationSpec': classificationSpec,
                'defaultLang': defaultLang,
                'delimiter': delimiter,
                'encoding': encoding,
                'featureSource': featureSource,
                'inputFormat': None if inputFormat is None else inputFormat.value,
                'mappingSpec': mappingSpec,
                'profile': profile,
                'quote': quote,
                'sourceCRS': sourceCRS,
                'targetCRS': targetCRS,
            },
        }

        return requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

    def transform_csv(
        self,
        path: str,
        **kwargs
    ) -> dict:
        """Transforms a CSV file to a RDF dataset.

        Args:
            path (str): The relative path to a file on the remote user file
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

        return self._transform(
            path,
            EnumDataFormat.CSV,
            **kwargs
        )

    def transform_shapefile(
        self,
        path: str,
        **kwargs
    ) -> dict:
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

        return self._transform(
            path,
            EnumDataFormat.SHAPEFILE,
            **kwargs
        )

    def _get_input(self, value: InputType) -> dict:
        if isinstance(value,  str):
            return {
                'type': EnumInputType.FILESYSTEM.value,
                'path': value,
            }
        if isinstance(value,  tuple):
            if(len(value) == 2):
                return {
                    'type': EnumInputType.CATALOG.value,
                    'id': value[0],
                    'version': value[1],
                }
            elif(len(value) == 3):
                return {
                    'type': EnumInputType.OUTPUT.value,
                    'processId': value[0],
                    'processVersion': value[1],
                    'fileId': value[2],
                }
            else:
                raise SlipoException(
                    'Expected a tuple with 2 or 3 members. Instead received {size}'.format(size=len(value)))
        raise SlipoException(
            'Unsupported input type {type}'.format(type=type(value)))

    @json_response
    def interlink(
        self,
        profile: str,
        left: InputType,
        right: InputType
    ) -> dict:
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
            left (Union[str, Tuple[int, int], Tuple[int, int, int]]): The `left` RDF dataset.
            right (Union[str, Tuple[int, int], Tuple[int, int, int]]): The `right` RDF dataset.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_INTERLINK.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        data = {
            'profile': profile,
            'left': self._get_input(left),
            'right': self._get_input(right),
        }

        return requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

    @json_response
    def fuse(
        self,
        profile: str,
        left: InputType,
        right: InputType,
        links: InputType
    ) -> dict:
        """Fuses two RDF datasets using Linked Data and returns a new RDF dataset.

        Args:
            profile (str): The name of the profile to use. Profile names can
                be retrieved using :meth:`profiles` method.
            left (Union[str, Tuple[int, int], Tuple[int, int, int]]): The `left` RDF dataset.
            right (Union[str, Tuple[int, int], Tuple[int, int, int]]): The `right` RDF dataset.
            links (Union[str, Tuple[int, int], Tuple[int, int, int]]): The links for the `left` and `right` datasets.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_FUSE.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        data = {
            'profile': profile,
            'left': self._get_input(left),
            'right': self._get_input(right),
            'links': self._get_input(links),
        }

        return requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

    @json_response
    def enrich(
        self,
        profile: str,
        source: InputType
    ) -> dict:
        """Enriches a RDF dataset.

        Args:
            profile (str): The name of the profile to use. Profile names can
                be retrieved using :meth:`profiles` method.
            source (Union[str, Tuple[int, int], Tuple[int, int, int]]): The RDF dataset to enrich.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_ENRICH.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        data = {
            'profile': profile,
            'input': self._get_input(source),
        }

        return requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

    @json_response
    def _export(
        self,
        profile: str,
        source: InputType,
        outputFormat: EnumDataFormat,
        defaultLang: str = 'en',
        delimiter: str = '|',
        encoding: str = 'UTF-8',
        quote: str = '\\"',
        sourceCRS: str = 'EPSG:4326',
        sparqlFile: str = None,
        targetCRS: str = 'EPSG:4326',
    ) -> dict:
        endpoint = API_EXPORT.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        data = {
            'input': self._get_input(source),
            'configuration': {
                'defaultLang': defaultLang,
                'delimiter': delimiter,
                'encoding': encoding,
                'outputFormat': None if outputFormat is None else outputFormat.value,
                'profile': profile,
                'quote': quote,
                'sourceCRS': sourceCRS,
                'sparqlFile': sparqlFile,
                'targetCRS': targetCRS,
            },
        }

        return requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

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
            source (Union[str, Tuple[int, int], Tuple[int, int, int]]): The RDF dataset
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

        return self._export(
            profile,
            source,
            EnumDataFormat.CSV,
            **kwargs
        )

    def export_shapefile(
        self,
        profile: str,
        source: InputType,
        **kwargs
    ) -> dict:
        """Exports a RDF dataset to a SHAPEFILE file.

        Args:
            profile (str): The name of the profile to use. Profile names can
                be retrieved using :meth:`profiles` method.
            source (Union[str, Tuple[int, int], Tuple[int, int, int]]): The RDF dataset
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

        return self._export(
            profile,
            source,
            EnumDataFormat.SHAPEFILE,
            **kwargs
        )
