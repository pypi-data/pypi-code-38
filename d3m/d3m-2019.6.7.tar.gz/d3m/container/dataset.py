import abc
import argparse
import collections
import datetime
import errno
import filecmp
import hashlib
import io
import itertools
import json
import logging
import math
import os
import os.path
import pprint
import shutil
import sys
import time
import traceback
import typing
from urllib import error as urllib_error, parse as url_parse

import dateparser  # type: ignore
import frozendict  # type: ignore
import networkx  # type: ignore
import numpy  # type: ignore
import pandas  # type: ignore
from pandas.io import common as pandas_io_common  # type: ignore
from sklearn import datasets  # type: ignore

from . import pandas as container_pandas
from d3m import deprecate, exceptions, utils
from d3m.metadata import base as metadata_base

# See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
try:
    from pyarrow import lib as pyarrow_lib  # type: ignore
except ModuleNotFoundError:
    pyarrow_lib = None

__all__ = ('Dataset', 'ComputeDigest')

logger = logging.getLogger(__name__)

UNITS = {
    'B': 1, 'KB': 10**3, 'MB': 10**6, 'GB': 10**9, 'TB': 10**12, 'PB': 10**15,
    'KiB': 2*10, 'MiB': 2*20, 'GiB': 2*30, 'TiB': 2*40, 'PiB': 2*50,
}
SIZE_TO_UNITS = {
    1: 'B', 3: 'KB', 6: 'MB',
    9: 'GB', 12: 'TB', 15: 'PB',
}

D3M_ROLE_CONSTANTS_TO_SEMANTIC_TYPES = {
    'index': 'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
    'multiIndex': 'https://metadata.datadrivendiscovery.org/types/PrimaryMultiKey',
    'key': 'https://metadata.datadrivendiscovery.org/types/UniqueKey',
    'attribute': 'https://metadata.datadrivendiscovery.org/types/Attribute',
    'suggestedTarget': 'https://metadata.datadrivendiscovery.org/types/SuggestedTarget',
    'timeIndicator': 'https://metadata.datadrivendiscovery.org/types/Time',
    'locationIndicator': 'https://metadata.datadrivendiscovery.org/types/Location',
    'boundaryIndicator': 'https://metadata.datadrivendiscovery.org/types/Boundary',
    'interval': 'https://metadata.datadrivendiscovery.org/types/Interval',
    'instanceWeight': 'https://metadata.datadrivendiscovery.org/types/InstanceWeight',
    'boundingPolygon': 'https://metadata.datadrivendiscovery.org/types/BoundingPolygon',
    'suggestedPrivilegedData': 'https://metadata.datadrivendiscovery.org/types/SuggestedPrivilegedData',
    'suggestedGroupingKey': 'https://metadata.datadrivendiscovery.org/types/SuggestedGroupingKey',
    'edgeSource': 'https://metadata.datadrivendiscovery.org/types/EdgeSource',
    'directedEdgeSource': 'https://metadata.datadrivendiscovery.org/types/DirectedEdgeSource',
    'undirectedEdgeSource': 'https://metadata.datadrivendiscovery.org/types/UndirectedEdgeSource',
    'simpleEdgeSource': 'https://metadata.datadrivendiscovery.org/types/SimpleEdgeSource',
    'multiEdgeSource': 'https://metadata.datadrivendiscovery.org/types/MultiEdgeSource',
    'edgeTarget': 'https://metadata.datadrivendiscovery.org/types/EdgeTarget',
    'directedEdgeTarget': 'https://metadata.datadrivendiscovery.org/types/DirectedEdgeTarget',
    'undirectedEdgeTarget': 'https://metadata.datadrivendiscovery.org/types/UndirectedEdgeTarget',
    'simpleEdgeTarget': 'https://metadata.datadrivendiscovery.org/types/SimpleEdgeTarget',
    'multiEdgeTarget': 'https://metadata.datadrivendiscovery.org/types/MultiEdgeTarget',
}

D3M_RESOURCE_TYPE_CONSTANTS_TO_SEMANTIC_TYPES = {
    # File collections.
    'image': 'http://schema.org/ImageObject',
    'video': 'http://schema.org/VideoObject',
    'audio': 'http://schema.org/AudioObject',
    'text': 'http://schema.org/Text',
    'speech': 'https://metadata.datadrivendiscovery.org/types/Speech',
    'timeseries': 'https://metadata.datadrivendiscovery.org/types/Timeseries',
    'raw': 'https://metadata.datadrivendiscovery.org/types/UnspecifiedStructure',
    # Other.
    'graph': 'https://metadata.datadrivendiscovery.org/types/Graph',
    'edgeList': 'https://metadata.datadrivendiscovery.org/types/EdgeList',
    'table': 'https://metadata.datadrivendiscovery.org/types/Table',
}

D3M_COLUMN_TYPE_CONSTANTS_TO_SEMANTIC_TYPES = {
    'boolean': 'http://schema.org/Boolean',
    'integer': 'http://schema.org/Integer',
    'real': 'http://schema.org/Float',
    'string': 'http://schema.org/Text',
    'categorical': 'https://metadata.datadrivendiscovery.org/types/CategoricalData',
    'dateTime': 'http://schema.org/DateTime',
    'realVector': 'https://metadata.datadrivendiscovery.org/types/FloatVector',
    'json': 'https://metadata.datadrivendiscovery.org/types/JSON',
    'geojson': 'https://metadata.datadrivendiscovery.org/types/GeoJSON',
    'unknown': 'https://metadata.datadrivendiscovery.org/types/UnknownType',
}

SEMANTIC_TYPES_TO_D3M_RESOURCE_TYPES = {v: k for k, v in D3M_RESOURCE_TYPE_CONSTANTS_TO_SEMANTIC_TYPES.items()}
SEMANTIC_TYPES_TO_D3M_ROLES = {v: k for k, v in D3M_ROLE_CONSTANTS_TO_SEMANTIC_TYPES.items()}
SEMANTIC_TYPES_TO_D3M_COLUMN_TYPES = {v: k for k, v in D3M_COLUMN_TYPE_CONSTANTS_TO_SEMANTIC_TYPES.items()}

D3M_TO_DATASET_FIELDS: typing.Dict[typing.Sequence[str], typing.Tuple[typing.Sequence[str], bool]] = {
    ('about', 'datasetID'): (('id',), True),
    ('about', 'datasetName'): (('name',), True),
    ('about', 'description'): (('description',), False),
    ('about', 'datasetVersion'): (('version',), False),
    ('about', 'digest'): (('digest',), False),
    ('about', 'approximateSize'): (('approximate_stored_size',), False),
    ('about', 'citation'): (('source', 'citation'), False),
    ('about', 'license'): (('source', 'license'), False),
    ('about', 'redacted'): (('source', 'redacted'), False),
    ('about', 'source'): (('source', 'name'), False),
    ('about', 'citation'): (('source', 'citation'), False),
    ('about', 'humanSubjectsResearch'): (('source', 'human_subjects_research'), False),
}

INTERVAL_SEMANTIC_TYPES = (
    'https://metadata.datadrivendiscovery.org/types/IntervalStart',
    'https://metadata.datadrivendiscovery.org/types/IntervalEnd',
)

BOUNDARY_SEMANTIC_TYPES = (
    'https://metadata.datadrivendiscovery.org/types/Interval',
    'https://metadata.datadrivendiscovery.org/types/BoundingPolygon',
) + INTERVAL_SEMANTIC_TYPES

# A map between D3M resource formats and media types.
MEDIA_TYPES = {
    'audio/aiff': 'audio/aiff',
    'audio/flac': 'audio/flac',
    'audio/ogg': 'audio/ogg',
    'audio/wav': 'audio/wav',
    'audio/mpeg': 'audio/mpeg',
    'image/jpeg': 'image/jpeg',
    'image/png': 'image/png',
    'video/mp4': 'video/mp4',
    'video/avi': 'video/avi',
    'text/csv': 'text/csv',
    'text/plain': 'text/plain',
    'text/gml': 'text/vnd.gml',
}
MEDIA_TYPES_REVERSE = {v: k for k, v in MEDIA_TYPES.items()}

# A map between D3M file extensions and media types.
# Based on: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/blob/shared/documentation/supportedResourceTypesFormats.json
FILE_EXTENSIONS = {
    '.aif': 'audio/aiff',
    '.aiff': 'audio/aiff',
    '.flac': 'audio/flac',
    '.ogg': 'audio/ogg',
    '.wav': 'audio/wav',
    '.mp3': 'audio/mpeg',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.csv': 'text/csv',
    '.gml': 'text/vnd.gml',
    '.txt': 'text/plain',
    '.mp4': 'video/mp4',
    '.avi': 'video/avi',
}

REFERENCE_MAP = {
    'node': 'NODE',
    'nodeAttribute': 'NODE_ATTRIBUTE',
    'edge': 'EDGE',
    'edgeAttribute': 'EDGE_ATTRIBUTE',
}
REFERENCE_MAP_REVERSE = {v: k for k, v in REFERENCE_MAP.items()}

ALL_D3M_SEMANTIC_TYPES = \
    set(D3M_ROLE_CONSTANTS_TO_SEMANTIC_TYPES.values()) | \
    set(D3M_RESOURCE_TYPE_CONSTANTS_TO_SEMANTIC_TYPES.values()) | \
    set(D3M_COLUMN_TYPE_CONSTANTS_TO_SEMANTIC_TYPES.values()) | \
    set(BOUNDARY_SEMANTIC_TYPES)

if not ALL_D3M_SEMANTIC_TYPES <= metadata_base.ALL_SEMANTIC_TYPES:
    raise ValueError("Not all D3M semantic types are defined in metadata.")


class ComputeDigest(utils.Enum):
    """
    Enumeration of possible approaches to computing dataset digest.
    """

    NEVER = 1
    ONLY_IF_MISSING = 2
    ALWAYS = 3


def parse_size(size_string: str) -> int:
    number, unit = [string.strip() for string in size_string.split()]
    return int(float(number) * UNITS[unit])


def is_simple_boundary(semantic_types: typing.Tuple[str]) -> bool:
    """
    A simple boundary is a column with only "https://metadata.datadrivendiscovery.org/types/Boundary"
    semantic type and no other.
    """

    return 'https://metadata.datadrivendiscovery.org/types/Boundary' in semantic_types and not any(boundary_semantic_type in semantic_types for boundary_semantic_type in BOUNDARY_SEMANTIC_TYPES)


def update_digest(hash: typing.Any, file_path: str) -> None:
    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(hash.block_size)
            if not chunk:
                break
            hash.update(chunk)


# This exists as a reference implementation for computing a digest of D3M dataset.
# Loader below does an equivalent computation as part of dataset loading process.
def get_d3m_dataset_digest(dataset_doc_path: str) -> str:
    hash = hashlib.sha256()

    with open(dataset_doc_path, 'r', encoding='utf8') as dataset_doc_file:
        dataset_doc = json.load(dataset_doc_file)

    dataset_path = os.path.dirname(dataset_doc_path)

    for data_resource in dataset_doc['dataResources']:
        if data_resource.get('isCollection', False):
            collection_path = os.path.join(dataset_path, data_resource['resPath'])

            # We assume that we can just concat "collection_path" with a value in the column.
            assert collection_path[-1] == '/'

            for filename in utils.list_files(collection_path):
                file_path = os.path.join(collection_path, filename)

                # We include both the filename and the content.
                hash.update(os.path.join(data_resource['resPath'], filename).encode('utf8'))
                update_digest(hash, file_path)

        else:
            resource_path = os.path.join(dataset_path, data_resource['resPath'])

            # We include both the filename and the content.
            hash.update(data_resource['resPath'].encode('utf8'))
            update_digest(hash, resource_path)

    # We remove digest, if it exists in dataset description, before computing the digest over the rest.
    dataset_doc['about'].pop('digest', None)

    # We add to hash also the dataset description, with sorted keys.
    hash.update(json.dumps(dataset_doc, sort_keys=True).encode('utf8'))

    return hash.hexdigest()


class Loader(metaclass=utils.AbstractMetaclass):
    """
    A base class for dataset loaders.
    """

    @abc.abstractmethod
    def can_load(self, dataset_uri: str) -> bool:
        """
        Return ``True`` if this loader can load a dataset from a given URI ``dataset_uri``.

        Parameters
        ----------
        dataset_uri : str
            A URI to load a dataset from.

        Returns
        -------
        bool
            ``True`` if this loader can load a dataset from ``dataset_uri``.
        """

    @abc.abstractmethod
    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, handle_score_split: bool = True) -> 'Dataset':
        """
        Loads the dataset at ``dataset_uri``.

        Parameters
        ----------
        dataset_uri : str
            A URI to load.
        dataset_id : str
            Override dataset ID determined by the loader.
        dataset_version : str
            Override dataset version determined by the loader.
        dataset_name : str
            Override dataset name determined by the loader.
        lazy : bool
            If ``True``, load only top-level metadata and not whole dataset.
        compute_digest : ComputeDigest
            Compute a digest over the data?
        strict_digest : bool
            If computed digest does not match the one provided in metadata, raise an exception?
        handle_score_split : bool
            If a scoring dataset has target values in a separate file, merge them in?

        Returns
        -------
        Dataset
            A loaded dataset.
        """


class Saver(metaclass=utils.AbstractMetaclass):
    """
    A base class for dataset savers.
    """

    @abc.abstractmethod
    def can_save(self, dataset_uri: str) -> bool:
        """
        Return ``True`` if this saver can save a dataset to a given URI ``dataset_uri``.

        Parameters
        ----------
        dataset_uri : str
            A URI to save a dataset to.

        Returns
        -------
        bool
            ``True`` if this saver can save a dataset to ``dataset_uri``.
        """

    @abc.abstractmethod
    def save(self, dataset: 'Dataset', dataset_uri: str, *, compute_digest: ComputeDigest = ComputeDigest.ALWAYS) -> None:
        """
        Saves the dataset ``dataset`` to ``dataset_uri``.

        Parameters
        ----------
        dataset : Dataset
            A dataset to save.
        dataset_uri : str
            A URI to save to.
        compute_digest : ComputeDigest
            Compute digest over the data when saving?
        """


class D3MDatasetLoader(Loader):
    """
    A class for loading of D3M datasets.

    Loader support only loading from a local file system.
    URI should point to the ``datasetDoc.json`` file in the D3M dataset directory.
    """

    SUPPORTED_VERSIONS = {'3.0', '3.1', '3.1.1', '3.1.2', '3.2.0', '3.2.1', '3.3.0', '3.3.1'}

    def can_load(self, dataset_uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(dataset_uri, allow_fragments=False)
        except Exception:
            return False

        if parsed_uri.scheme != 'file':
            return False

        if parsed_uri.netloc not in ['', 'localhost']:
            return False

        if not parsed_uri.path.startswith('/'):
            return False

        if os.path.basename(parsed_uri.path) != 'datasetDoc.json':
            return False

        return True

    def _load_data(self, resources: typing.Dict, metadata: metadata_base.DataMetadata, *, dataset_path: str, dataset_doc: typing.Dict,
                   dataset_id: typing.Optional[str], dataset_digest: typing.Optional[str],
                   compute_digest: ComputeDigest, strict_digest: bool, handle_score_split: bool) -> typing.Tuple[metadata_base.DataMetadata, typing.Optional[str]]:
        # Allowing "True" for backwards compatibility.
        if compute_digest is True or compute_digest == ComputeDigest.ALWAYS or (compute_digest == ComputeDigest.ONLY_IF_MISSING and dataset_digest is None):
            hash = hashlib.sha256()
        else:
            hash = None

        for data_resource in dataset_doc['dataResources']:
            if data_resource.get('isCollection', False):
                resources[data_resource['resID']], metadata = self._load_collection(dataset_path, data_resource, metadata, hash)
            else:
                loader = getattr(self, '_load_resource_type_{resource_type}'.format(resource_type=data_resource['resType']), None)
                if loader is None:
                    raise exceptions.NotSupportedError("Resource type '{resource_type}' is not supported.".format(resource_type=data_resource['resType']))

                resources[data_resource['resID']], metadata = loader(dataset_path, data_resource, metadata, hash)

        # Backwards compatibility. If there is no resource marked as a dataset entry point,
        # check if there is any resource with a suitable filename.
        for data_resource in dataset_doc['dataResources']:
            if metadata.has_semantic_type((data_resource['resID'],), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint'):
                break
        else:
            for data_resource in dataset_doc['dataResources']:
                if os.path.splitext(os.path.basename(data_resource['resPath']))[0] == 'learningData':
                    metadata = metadata.add_semantic_type((data_resource['resID'],), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint')

        # Handle a special case for SCORE dataset splits (those which have "targets.csv" file).
        # They are the same as TEST dataset splits, but we present them differently, so that
        # SCORE dataset splits have targets as part of data.
        # See: https://gitlab.com/datadrivendiscovery/d3m/issues/176
        if handle_score_split and os.path.exists(os.path.join(dataset_path, '..', 'targets.csv')):
            self._merge_score_targets(resources, metadata, dataset_path, hash)

        if hash is not None:
            # We remove digest, if it exists in dataset description, before computing the digest over the rest.
            # We modify "dataset_doc" here, but this is OK, we do not need it there anymore at this point.
            dataset_doc['about'].pop('digest', None)

            # We add to hash also the dataset description, with sorted keys.
            hash.update(json.dumps(dataset_doc, sort_keys=True).encode('utf8'))

            new_dataset_digest = hash.hexdigest()

            if dataset_digest is not None and dataset_digest != new_dataset_digest:
                if strict_digest:
                    raise exceptions.DigestMismatchError(
                        "Digest for dataset '{dataset_id}' does not match one from dataset description. Dataset description digest: {dataset_digest}. Computed digest: {new_dataset_digest}.".format(
                            dataset_id=dataset_id or dataset_doc['about']['datasetID'],
                            dataset_digest=dataset_digest,
                            new_dataset_digest=new_dataset_digest,
                        )
                    )
                else:
                    logger.warning(
                        "Digest for dataset '%(dataset_id)s' does not match one from dataset description. Dataset description digest: %(dataset_digest)s. Computed digest: %(new_dataset_digest)s.",
                        {
                            'dataset_id': dataset_id or dataset_doc['about']['datasetID'],
                            'dataset_digest': dataset_digest,
                            'new_dataset_digest': new_dataset_digest,
                        },
                    )
        else:
            new_dataset_digest = dataset_doc['about'].get('digest', None)

        return metadata, new_dataset_digest

    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, handle_score_split: bool = True) -> 'Dataset':
        assert self.can_load(dataset_uri)

        parsed_uri = url_parse.urlparse(dataset_uri, allow_fragments=False)

        dataset_doc_path = parsed_uri.path
        dataset_path = os.path.dirname(dataset_doc_path)

        try:
            with open(dataset_doc_path, 'r', encoding='utf8') as dataset_doc_file:
                dataset_doc = json.load(dataset_doc_file)
        except FileNotFoundError as error:
            raise exceptions.DatasetNotFoundError(
                "D3M dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri),
            ) from error

        dataset_schema_version = dataset_doc.get('about', {}).get('datasetSchemaVersion', '3.3.0')
        if dataset_schema_version not in self.SUPPORTED_VERSIONS:
            logger.warning("Loading a dataset with unsupported schema version '%(version)s'. Supported versions: %(supported_versions)s", {
                'version': dataset_schema_version,
                'supported_versions': self.SUPPORTED_VERSIONS,
            })

        # We do not compute digest here, but we use one from dataset description if it exist.
        # This is different from other loaders which compute digest when lazy loading and check
        # it after data is finally loaded to make sure data has not changed in meantime.
        dataset_digest = dataset_doc['about'].get('digest', None)

        resources: typing.Dict = {}
        metadata = metadata_base.DataMetadata()

        if not lazy:
            load_lazy = None

            metadata, dataset_digest = self._load_data(
                resources, metadata, dataset_path=dataset_path, dataset_doc=dataset_doc, dataset_id=dataset_id,
                dataset_digest=dataset_digest, compute_digest=compute_digest, strict_digest=strict_digest,
                handle_score_split=handle_score_split,
            )

            metadata = self._load_qualities(dataset_doc, metadata)

        else:
            def load_lazy(dataset: Dataset) -> None:
                nonlocal dataset_digest

                # "dataset" can be used as "resources", it is a dict of values.
                dataset.metadata, dataset_digest = self._load_data(
                    dataset, dataset.metadata, dataset_path=dataset_path, dataset_doc=dataset_doc, dataset_id=dataset_id,
                    dataset_digest=dataset_digest, compute_digest=compute_digest, strict_digest=strict_digest,
                    handle_score_split=handle_score_split,
                )

                dataset.metadata = self._load_qualities(dataset_doc, dataset.metadata)

                new_metadata = {
                    'dimension': {'length': len(dataset)},
                }

                if dataset_digest is not None:
                    new_metadata['digest'] = dataset_digest

                dataset.metadata = dataset.metadata.update((), new_metadata)
                dataset.metadata = dataset.metadata.generate(dataset)

                dataset._load_lazy = None

        document_dataset_id = dataset_doc['about']['datasetID']
        # Handle a special case for SCORE dataset splits (those which have "targets.csv" file).
        # They are the same as TEST dataset splits, but we present them differently, so that
        # SCORE dataset splits have targets as part of data. Because of this we also update
        # corresponding dataset ID.
        # See: https://gitlab.com/datadrivendiscovery/d3m/issues/176
        if handle_score_split and os.path.exists(os.path.join(dataset_path, '..', 'targets.csv')) and document_dataset_id.endswith('_TEST'):
            document_dataset_id = document_dataset_id[:-5] + '_SCORE'

        dataset_metadata = {
            'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or document_dataset_id,
            'version': dataset_version or dataset_doc['about'].get('datasetVersion', '1.0'),
            'name': dataset_name or dataset_doc['about']['datasetName'],
            'location_uris': [
                # We reconstruct the URI to normalize it.
                utils.fix_uri(dataset_doc_path),
            ],
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        if dataset_digest is not None:
            dataset_metadata['digest'] = dataset_digest

        if dataset_doc['about'].get('description', None):
            dataset_metadata['description'] = dataset_doc['about']['description']

        if dataset_doc['about'].get('approximateSize', None):
            try:
                dataset_metadata['approximate_stored_size'] = parse_size(dataset_doc['about']['approximateSize'])
            except Exception as error:
                raise ValueError("Unable to parse 'approximateSize': {approximate_size}".format(approximate_size=dataset_doc['about']['approximateSize'])) from error

        if dataset_doc['about'].get('datasetURI', None):
            typing.cast(typing.List[str], dataset_metadata['location_uris']).append(dataset_doc['about']['datasetURI'])

        dataset_source = {
            'redacted': dataset_doc['about'].get('redacted', False),
        }

        # "license" is often an empty string and in that case we do not want
        # really to set the field in dataset metadata.
        if dataset_doc['about'].get('license', None):
            dataset_source['license'] = dataset_doc['about']['license']

        if 'humanSubjectsResearch' in dataset_doc['about']:
            dataset_source['human_subjects_research'] = dataset_doc['about']['humanSubjectsResearch']

        if dataset_doc['about'].get('source', None):
            dataset_source['name'] = dataset_doc['about']['source']

        if dataset_doc['about'].get('citation', None):
            dataset_source['citation'] = dataset_doc['about']['citation']

        if dataset_doc['about'].get('publicationDate', None):
            try:
                # If no timezone information is provided, we assume UTC. If there is timezone information, we convert
                # timestamp to UTC, but then remove timezone information before formatting to not have "+00:00" added
                # and we then manually add "Z" instead (which has equivalent meaning).
                dataset_source['published'] = dateparser.parse(dataset_doc['about']['publicationDate'], settings={'TIMEZONE': 'UTC'}).replace(tzinfo=None).isoformat('T') + 'Z'
            except Exception as error:
                raise ValueError("Unable to parse 'publicationDate': {publication_date}".format(publication_date=dataset_doc['about']['publicationDate'])) from error

        if dataset_doc['about'].get('sourceURI', None):
            dataset_source['uris'] = [dataset_doc['about']['sourceURI']]

        dataset_metadata['source'] = dataset_source

        if dataset_doc['about'].get('applicationDomain', None):
            # Application domain has no vocabulary specified so we map it to keywords.
            dataset_metadata['keywords'] = [dataset_doc['about']['applicationDomain']]

        metadata = metadata.update((), dataset_metadata)

        # TODO: Add loading of all other metadata which is not part of D3M schema from qualities.
        #       See: https://gitlab.com/datadrivendiscovery/d3m/issues/227

        return Dataset(resources, metadata, load_lazy=load_lazy)

    def _load_qualities(self, dataset_doc: typing.Dict, metadata: metadata_base.DataMetadata) -> metadata_base.DataMetadata:
        # An alternative way to describe LUPI datasets using process D3M qualities.
        # See: https://gitlab.com/datadrivendiscovery/d3m/issues/61
        #      https://gitlab.com/datadrivendiscovery/d3m/issues/225
        for quality in dataset_doc.get('qualities', []):
            if quality['qualName'] != 'privilegedFeature':
                continue

            if quality['qualValue'] != 'True':
                continue

            restricted_to = quality.get('restrictedTo', {})

            column_index = restricted_to.get('resComponent', {}).get('columnIndex', None)
            if column_index is not None:
                metadata = self._add_semantic_type_for_column_index(metadata, restricted_to['resID'], column_index, 'https://metadata.datadrivendiscovery.org/types/SuggestedPrivilegedData')
                continue

            column_name = restricted_to.get('resComponent', {}).get('columnName', None)
            if column_name is not None:
                metadata = self._add_semantic_type_for_column_name(metadata, restricted_to['resID'], column_name, 'https://metadata.datadrivendiscovery.org/types/SuggestedPrivilegedData')
                continue

        return metadata

    def _add_semantic_type_for_column_index(self, metadata: metadata_base.DataMetadata, resource_id: str, column_index: int, semantic_type: str) -> metadata_base.DataMetadata:
        return metadata.add_semantic_type((resource_id, metadata_base.ALL_ELEMENTS, column_index), semantic_type)

    def _add_semantic_type_for_column_name(self, metadata: metadata_base.DataMetadata, resource_id: str, column_name: str, semantic_type: str) -> metadata_base.DataMetadata:
        column_index = metadata.get_column_index_from_column_name(column_name, at=(resource_id,))

        return self._add_semantic_type_for_column_index(metadata, resource_id, column_index, semantic_type)

    def _load_collection(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata,
                         hash: typing.Any) -> typing.Tuple[container_pandas.DataFrame, metadata_base.DataMetadata]:
        assert data_resource.get('isCollection', False)

        collection_path = os.path.join(dataset_path, data_resource['resPath'])

        # We allow unknown formats here, but it will probably fail when resolving file extensions.
        all_media_types = [MEDIA_TYPES.get(format, format) for format in data_resource['resFormat']]
        all_media_types_set = set(all_media_types)

        filenames = []
        media_types = []

        for filename in utils.list_files(collection_path):
            file_path = os.path.join(collection_path, filename)

            filename_extension = os.path.splitext(filename)[1]

            filenames.append(filename)

            try:
                media_type = FILE_EXTENSIONS[filename_extension]
            except KeyError as error:
                raise TypeError("Unsupported file extension for file '{filename}'.".format(filename=filename)) from error

            if media_type not in all_media_types_set:
                raise TypeError("Unexpected media type '{media_type}' for file '{filename}'. Expected {all_media_types}.".format(
                    media_type=media_type, filename=filename, all_media_types=all_media_types,
                ))

            media_types.append(media_type)

            if hash is not None:
                # We include both the filename and the content.
                hash.update(os.path.join(data_resource['resPath'], filename).encode('utf8'))
                update_digest(hash, file_path)

        data = container_pandas.DataFrame({'filename': filenames}, columns=['filename'], dtype=object)

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/Table',
                'https://metadata.datadrivendiscovery.org/types/FilesCollection',
            ],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': 1,
            },
        })

        location_base_uri = utils.fix_uri(collection_path)
        # We want to make sure you can just concat with the filename.
        if not location_base_uri.endswith('/'):
            location_base_uri += '/'

        media_types_set = set(media_types)

        extra_media_types = all_media_types_set - media_types_set
        if extra_media_types:
            logger.warning("File collection '%(resource_id)s' claims more file formats than are used in files. Extraneous formats: %(formats)s", {
                'resource_id': data_resource['resID'],
                'formats': [MEDIA_TYPES_REVERSE.get(format, format) for format in sorted(extra_media_types)],
            })

        # Normalize the list based on real media types used.
        all_media_types = sorted(media_types_set)

        column_metadata = {
            'name': 'filename',
            'structural_type': str,
            'location_base_uris': [
                location_base_uri,
            ],
            # A superset of all media types of files in this collection.
            'media_types': all_media_types,
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
                'https://metadata.datadrivendiscovery.org/types/FileName',
                D3M_RESOURCE_TYPE_CONSTANTS_TO_SEMANTIC_TYPES[data_resource['resType']],
            ],
        }

        if data_resource.get('columns', None):
            columns_metadata = []

            for column in data_resource['columns']:
                columns_metadata.append(self._get_column_metadata(column))
                columns_metadata[-1]['name'] = column['colName']

            column_metadata['file_columns'] = columns_metadata

        metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS, 0), column_metadata)

        # If there are different rows with different media types, we have to set
        # on each row which media type it is being used.
        if len(all_media_types) > 1:
            # The following modifies metadata for rows directly instead of through metadata methods
            # to achieve useful performance because some datasets contain many files which means many
            # rows have their "media_types" set. Setting it one by one makes things to slow.
            # Here we are taking advantage of quite few assumptions: we are modifying metadata in-place
            # because we know it is only us having a reference to it, we directly set metadata for
            # rows because we know no other metadata exists for rows, moreover, we also know no other
            # metadata exists for rows through any higher ALL_ELEMENTS.
            # TODO: Expose this as a general metadata method.

            resource_metadata_entry = metadata._current_metadata.elements[data_resource['resID']]
            resource_row_elements_evolver = resource_metadata_entry.elements.evolver()
            resource_row_elements_evolver._reallocate(2 * len(media_types))
            for i, media_type in enumerate(media_types):
                column_metadata_entry = metadata_base.MetadataEntry(
                    metadata=frozendict.FrozenOrderedDict({
                        # A media type of this particular file.
                        'media_types': (media_type,),
                    }),
                    is_empty=False,
                )

                row_metadata_entry = metadata_base.MetadataEntry(
                    elements=utils.EMPTY_PMAP.set(0, column_metadata_entry),
                    is_empty=False,
                    is_elements_empty=False,
                )

                resource_row_elements_evolver.set(i, row_metadata_entry)

            resource_metadata_entry.elements = resource_row_elements_evolver.persistent()
            resource_metadata_entry.is_elements_empty = not resource_metadata_entry.elements
            resource_metadata_entry.update_is_empty()

        return data, metadata

    def _load_resource_type_table(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata,
                                  hash: typing.Any) -> typing.Tuple[container_pandas.DataFrame, metadata_base.DataMetadata]:
        assert not data_resource.get('isCollection', False)

        data = None
        column_names = None
        data_path = os.path.join(dataset_path, data_resource['resPath'])

        expected_names = None
        if data_resource.get('columns', None):
            expected_names = []
            for i, column in enumerate(data_resource['columns']):
                assert i == column['colIndex'], (i, column['colIndex'])
                expected_names.append(column['colName'])

        if data_resource['resFormat'] == ['text/csv']:
            data = pandas.read_csv(
                data_path,
                usecols=expected_names,
                # We do not want to do any conversion of values at this point.
                # This should be done by primitives later on.
                dtype=str,
                # We always expect one row header.
                header=0,
                # We want empty strings and not NaNs.
                na_filter=False,
                encoding='utf8',
                low_memory=False,
                memory_map=True,
            )

            column_names = list(data.columns)

            if expected_names is not None and expected_names != column_names:
                raise ValueError("Mismatch between column names in data {column_names} and expected names {expected_names}.".format(
                    column_names=column_names,
                    expected_names=expected_names,
                ))

            if hash is not None:
                # We include both the filename and the content.
                # TODO: Currently we read the file twice, once for reading and once to compute digest. Could we do it in one pass? Would it make it faster?
                hash.update(data_resource['resPath'].encode('utf8'))
                update_digest(hash, data_path)

        else:
            raise exceptions.NotSupportedError("Resource format '{resource_format}' for table '{resource_path}' is not supported.".format(
                resource_format=data_resource['resFormat'],
                resource_path=data_resource['resPath'],
            ))

        if data is None:
            raise FileNotFoundError("Data file for table '{resource_path}' cannot be found.".format(
                resource_path=data_resource['resPath'],
            ))

        data = container_pandas.DataFrame(data)

        assert column_names is not None

        semantic_types = [D3M_RESOURCE_TYPE_CONSTANTS_TO_SEMANTIC_TYPES[data_resource['resType']]]

        if data_resource['resID'] == 'learningData':
            semantic_types.append('https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint')

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': semantic_types,
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(column_names),
            },
        })

        for i, column_name in enumerate(column_names):
            metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS, i), {
                'name': column_name,
                'structural_type': str,
            })

        if expected_names is not None:
            for i, column in enumerate(data_resource['columns']):
                column_metadata = self._get_column_metadata(column)

                if 'https://metadata.datadrivendiscovery.org/types/Boundary' in column_metadata['semantic_types'] and 'boundary_for' not in column_metadata:
                    # Let's reconstruct for which column this is a boundary: currently
                    # this seems to be the first non-boundary column before this one.
                    for column_index in range(i - 1, 0, -1):
                        column_semantic_types = metadata.query((data_resource['resID'], metadata_base.ALL_ELEMENTS, column_index)).get('semantic_types', ())
                        if 'https://metadata.datadrivendiscovery.org/types/Boundary' not in column_semantic_types:
                            column_metadata['boundary_for'] = {
                                'resource_id': data_resource['resID'],
                                'column_index': column_index,
                            }
                            break

                metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS, i), column_metadata)

            current_boundary_start = None
            current_boundary_list: typing.Tuple[str, ...] = None
            column_index = 0
            while column_index < len(data_resource['columns']):
                column_semantic_types = metadata.query((data_resource['resID'], metadata_base.ALL_ELEMENTS, column_index)).get('semantic_types', ())
                if is_simple_boundary(column_semantic_types):
                    # Let's reconstruct which type of a boundary this is. Heuristic is simple.
                    # If there are two boundary columns next to each other, it is an interval.
                    if current_boundary_start is None:
                        assert current_boundary_list is None

                        count = 1
                        for next_column_index in range(column_index + 1, len(data_resource['columns'])):
                            if is_simple_boundary(metadata.query((data_resource['resID'], metadata_base.ALL_ELEMENTS, next_column_index)).get('semantic_types', ())):
                                count += 1
                            else:
                                break

                        if count == 2:
                            current_boundary_start = column_index
                            current_boundary_list = INTERVAL_SEMANTIC_TYPES
                        else:
                            # Unsupported group of boundary columns, let's skip them all.
                            column_index += count
                            continue

                    column_semantic_types = column_semantic_types + (current_boundary_list[column_index - current_boundary_start],)
                    metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS, column_index), {
                        'semantic_types': column_semantic_types,
                    })

                    if column_index - current_boundary_start + 1 == len(current_boundary_list):
                        current_boundary_start = None
                        current_boundary_list = None

                column_index += 1

        return data, metadata

    def _load_resource_type_edgeList(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata,
                                     hash: typing.Any) -> typing.Tuple[container_pandas.DataFrame, metadata_base.DataMetadata]:
        assert not data_resource.get('isCollection', False)

        return self._load_resource_type_table(dataset_path, data_resource, metadata, hash)

    def _load_resource_type_graph(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata, hash: typing.Any) -> \
            typing.Tuple[typing.Union[networkx.classes.graph.Graph, networkx.classes.digraph.DiGraph, networkx.classes.multigraph.MultiGraph,
                                      networkx.classes.multidigraph.MultiDiGraph], metadata_base.DataMetadata]:
        assert not data_resource.get('isCollection', False)

        data = None
        data_path = os.path.join(dataset_path, data_resource['resPath'])

        if data_resource['resFormat'] == ['text/gml']:
            data = networkx.read_gml(data_path, label='id')

            if hash is not None:
                # We include both the filename and the content.
                # TODO: Currently we read the file twice, once for reading and once to compute digest. Could we do it in one pass? Would it make it faster?
                hash.update(data_resource['resPath'].encode('utf8'))
                update_digest(hash, data_path)

        else:
            raise exceptions.NotSupportedError("Resource format '{resource_format}' for graph '{resource_path}' is not supported.".format(
                resource_format=data_resource['resFormat'],
                resource_path=data_resource['resPath']
            ))

        if data is None:
            raise FileNotFoundError("Data file for graph '{resource_path}' cannot be found.".format(
                resource_path=data_resource['resPath']
            ))

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': [D3M_RESOURCE_TYPE_CONSTANTS_TO_SEMANTIC_TYPES[data_resource['resType']]],
            'dimension': {
                'name': 'nodes',
                'length': len(data),
            },
        })

        return data, metadata

    def _get_column_metadata(self, column: typing.Dict) -> typing.Dict:
        semantic_types = [D3M_COLUMN_TYPE_CONSTANTS_TO_SEMANTIC_TYPES[column['colType']]]

        for role in column['role']:
            semantic_types.append(D3M_ROLE_CONSTANTS_TO_SEMANTIC_TYPES[role])

        # Suggested target is an attribute by default.
        if 'https://metadata.datadrivendiscovery.org/types/SuggestedTarget' in semantic_types and 'https://metadata.datadrivendiscovery.org/types/Attribute' not in semantic_types:
            semantic_types.append('https://metadata.datadrivendiscovery.org/types/Attribute')

        # Suggested privileged data is an attribute by default.
        if 'https://metadata.datadrivendiscovery.org/types/SuggestedPrivilegedData' in semantic_types and 'https://metadata.datadrivendiscovery.org/types/Attribute' not in semantic_types:
            semantic_types.append('https://metadata.datadrivendiscovery.org/types/Attribute')

        column_metadata: typing.Dict[str, typing.Any] = {
            'semantic_types': semantic_types,
        }

        if column.get('colDescription', None):
            column_metadata['description'] = column['colDescription']

        if column.get('refersTo', None):
            if isinstance(column['refersTo']['resObject'], str):
                if column['refersTo']['resObject'] == 'item':
                    # We represent collections as a table with one column of filenames.
                    column_metadata['foreign_key'] = {
                        'type': 'COLUMN',
                        'resource_id': column['refersTo']['resID'],
                        'column_index': 0,
                    }
                elif column['refersTo']['resObject'] in REFERENCE_MAP:
                    column_metadata['foreign_key'] = {
                        'type': REFERENCE_MAP[column['refersTo']['resObject']],
                        'resource_id': column['refersTo']['resID'],
                    }
                else:
                    raise exceptions.UnexpectedValueError("Unknown \"resObject\" value: {resource_object}".format(resource_object=column['refersTo']['resObject']))
            else:
                if 'columnIndex' in column['refersTo']['resObject']:
                    if 'https://metadata.datadrivendiscovery.org/types/Boundary' in semantic_types:
                        column_metadata['boundary_for'] = {
                            'resource_id': column['refersTo']['resID'],
                            'column_index': column['refersTo']['resObject']['columnIndex'],
                        }
                    else:
                        column_metadata['foreign_key'] = {
                            'type': 'COLUMN',
                            'resource_id': column['refersTo']['resID'],
                            'column_index': column['refersTo']['resObject']['columnIndex'],
                        }
                elif 'columnName' in column['refersTo']['resObject']:
                    if 'https://metadata.datadrivendiscovery.org/types/Boundary' in semantic_types:
                        column_metadata['boundary_for'] = {
                            'resource_id': column['refersTo']['resID'],
                            'column_name': column['refersTo']['resObject']['columnName'],
                        }
                    else:
                        column_metadata['foreign_key'] = {
                            'type': 'COLUMN',
                            'resource_id': column['refersTo']['resID'],
                            'column_name': column['refersTo']['resObject']['columnName'],
                        }
                else:
                    raise exceptions.UnexpectedValueError("Unknown \"resObject\" value: {resource_object}".format(resource_object=column['refersTo']['resObject']))

        return column_metadata

    def _merge_score_targets(self, resources: typing.Dict, metadata: metadata_base.DataMetadata, dataset_path: str, hash: typing.Any) -> None:
        targets_path = os.path.join(dataset_path, '..', 'targets.csv')

        targets = pandas.read_csv(
            targets_path,
            # We do not want to do any conversion of values at this point.
            # This should be done by primitives later on.
            dtype=str,
            # We always expect one row header.
            header=0,
            # We want empty strings and not NaNs.
            na_filter=False,
            encoding='utf8',
            low_memory=False,
            memory_map=True,
        )

        for resource_id, resource in resources.items():
            # We assume targets are only in the dataset entry point.
            if metadata.has_semantic_type((resource_id,), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint'):
                # We first make sure targets match resource in row order. At this stage all values
                # are strings, so we can fill simply with empty strings if it happens that index
                # values do not match (which in fact should never happen).
                reindexed_targets = targets.set_index('d3mIndex').reindex(resource.loc[:, 'd3mIndex'], fill_value='').reset_index()

                for column_name in reindexed_targets.columns:
                    if column_name == 'd3mIndex':
                        continue

                    # We match columns based on their names.
                    if column_name in resource.columns:
                        resource.loc[:, column_name] = reindexed_targets.loc[:, column_name]

                resources[resource_id] = resource


class CSVLoader(Loader):
    """
    A class for loading a dataset from a CSV file.

    Loader supports both loading a dataset from a local file system or remote locations.
    URI should point to a file with ``.csv`` file extension.
    """

    def can_load(self, dataset_uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(dataset_uri, allow_fragments=False)
        except Exception:
            return False

        if parsed_uri.scheme not in pandas_io_common._VALID_URLS:
            return False

        if parsed_uri.scheme == 'file':
            if parsed_uri.netloc not in ['', 'localhost']:
                return False

            if not parsed_uri.path.startswith('/'):
                return False

        for extension in ('', '.gz', '.bz2', '.zip', 'xz'):
            if parsed_uri.path.endswith('.csv' + extension):
                return True

        return False

    def _load_data(self, resources: typing.Dict, metadata: metadata_base.DataMetadata, *, dataset_uri: str,
                   compute_digest: ComputeDigest) -> typing.Tuple[metadata_base.DataMetadata, int, typing.Optional[str]]:
        try:
            buffer, compression, should_close = self._get_buffer_and_compression(dataset_uri)
        except FileNotFoundError as error:
            raise exceptions.DatasetNotFoundError("CSV dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri)) from error
        except urllib_error.HTTPError as error:
            if error.code == 404:
                raise exceptions.DatasetNotFoundError("CSV dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri)) from error
            else:
                raise error
        except urllib_error.URLError as error:
            if isinstance(error.reason, FileNotFoundError):
                raise exceptions.DatasetNotFoundError("CSV dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri)) from error
            else:
                raise error

        # CSV files do not have digest, so "ALWAYS" and "ONLY_IF_MISSING" is the same.
        # Allowing "True" for backwards compatibility.
        if compute_digest is True or compute_digest == ComputeDigest.ALWAYS or compute_digest == ComputeDigest.ONLY_IF_MISSING:
            buffer_digest = self._get_digest(buffer)
        else:
            buffer_digest = None

        buffer_size = len(buffer.getvalue())

        data = pandas.read_csv(
            buffer,
            # We do not want to do any conversion of values at this point.
            # This should be done by primitives later on.
            dtype=str,
            # We always expect one row header.
            header=0,
            # We want empty strings and not NaNs.
            na_filter=False,
            compression=compression,
            encoding='utf8',
            low_memory=False,
        )

        if should_close:
            try:
                buffer.close()
            except Exception:
                pass

        if 'd3mIndex' not in data.columns:
            # We do not update digest with new data generated here. This is OK because this data is determined by
            # original data so original digest still applies. When saving a new digest has to be computed anyway
            # because this data will have to be converted to string.
            data.insert(0, 'd3mIndex', range(len(data)))
            d3m_index_generated = True
        else:
            d3m_index_generated = False

        data = container_pandas.DataFrame(data)

        resources['learningData'] = data

        metadata = metadata.update(('learningData',), {
            'structural_type': type(data),
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/Table',
                'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint',
            ],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(data.columns),
            },
        })

        for i, column_name in enumerate(data.columns):
            if i == 0 and d3m_index_generated:
                metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS, i), {
                    'name': column_name,
                    'structural_type': numpy.int64,
                    'semantic_types': [
                        'http://schema.org/Integer',
                        'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
                    ],
                })
            else:
                metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS, i), {
                    'name': column_name,
                    'structural_type': str,
                    'semantic_types': [
                        'https://metadata.datadrivendiscovery.org/types/UnknownType',
                    ],
                })

        return metadata, buffer_size, buffer_digest

    def _get_buffer_and_compression(self, dataset_uri: str) -> typing.Tuple[io.BytesIO, str, bool]:
        compression = pandas_io_common._infer_compression(dataset_uri, 'infer')
        buffer, _, compression, should_close = pandas_io_common.get_filepath_or_buffer(dataset_uri, 'utf8', compression)

        return buffer, compression, should_close

    def _get_digest(self, buffer: io.BytesIO) -> str:
        return hashlib.sha256(buffer.getvalue()).hexdigest()

    # "strict_digest" is ignored, there is no metadata to compare digest against.
    # "handle_score_split" is ignored as well.
    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, handle_score_split: bool = True) -> 'Dataset':
        assert self.can_load(dataset_uri)

        parsed_uri = url_parse.urlparse(dataset_uri, allow_fragments=False)

        # Pandas requires a host for "file" URIs.
        if parsed_uri.scheme == 'file' and parsed_uri.netloc == '':
            parsed_uri = parsed_uri._replace(netloc='localhost')
            dataset_uri = url_parse.urlunparse(parsed_uri)

        dataset_size = None
        dataset_digest = None

        resources: typing.Dict = {}
        metadata = metadata_base.DataMetadata()

        if not lazy:
            load_lazy = None

            metadata, dataset_size, dataset_digest = self._load_data(
                resources, metadata, dataset_uri=dataset_uri, compute_digest=compute_digest,
            )

        else:
            def load_lazy(dataset: Dataset) -> None:
                # "dataset" can be used as "resources", it is a dict of values.
                dataset.metadata, dataset_size, dataset_digest = self._load_data(
                    dataset, dataset.metadata, dataset_uri=dataset_uri, compute_digest=compute_digest,
                )

                new_metadata = {
                    'dimension': {'length': len(dataset)},
                    'stored_size': dataset_size,
                }

                if dataset_digest is not None:
                    new_metadata['digest'] = dataset_digest

                dataset.metadata = dataset.metadata.update((), new_metadata)
                dataset.metadata = dataset.metadata.generate(dataset)

                dataset._load_lazy = None

        dataset_metadata = {
            'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or dataset_uri,
            'name': dataset_name or os.path.basename(parsed_uri.path),
            'location_uris': [
                dataset_uri,
            ],
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        if dataset_version is not None:
            dataset_metadata['version'] = dataset_version

        if dataset_size is not None:
            dataset_metadata['stored_size'] = dataset_size

        if dataset_digest is not None:
            dataset_metadata['digest'] = dataset_digest

        metadata = metadata.update((), dataset_metadata)

        return Dataset(resources, metadata, load_lazy=load_lazy)


class SklearnExampleLoader(Loader):
    """
    A class for loading example scikit-learn datasets.

    URI should be of the form ``sklearn://<name of the dataset>``, where names come from
    ``sklearn.datasets.load_*`` function names.
    """

    def can_load(self, dataset_uri: str) -> bool:
        if dataset_uri.startswith('sklearn://'):
            return True

        return False

    def _load_data(self, resources: typing.Dict, metadata: metadata_base.DataMetadata, *, dataset_path: str,
                   compute_digest: ComputeDigest) -> typing.Tuple[metadata_base.DataMetadata, typing.Optional[str], typing.Optional[str]]:
        bunch = self._get_bunch(dataset_path)

        # Sklearn datasets do not have digest, so "ALWAYS" and "ONLY_IF_MISSING" is the same.
        # Allowing "True" for backwards compatibility.
        if compute_digest is True or compute_digest == ComputeDigest.ALWAYS or compute_digest == ComputeDigest.ONLY_IF_MISSING:
            bunch_digest = self._get_digest(bunch)
        else:
            bunch_digest = None

        bunch_description = bunch.get('DESCR', None) or None

        bunch_data = bunch['data']
        bunch_target = bunch['target']

        if len(bunch_data.shape) == 1:
            bunch_data = bunch_data.reshape((bunch_data.shape[0], 1))
        if len(bunch_target.shape) == 1:
            bunch_target = bunch_target.reshape((bunch_target.shape[0], 1))

        column_names = []
        target_values = None

        if 'feature_names' in bunch:
            for feature_name in bunch['feature_names']:
                column_names.append(str(feature_name))

        if 'target_names' in bunch:
            if len(bunch['target_names']) == bunch_target.shape[1]:
                for target_name in bunch['target_names']:
                    column_names.append(str(target_name))
            else:
                target_values = [str(target_value) for target_value in bunch['target_names']]

        if target_values is not None:
            converted_target = numpy.empty(bunch_target.shape, dtype=object)

            for i, row in enumerate(bunch_target):
                for j, column in enumerate(row):
                    converted_target[i, j] = target_values[column]
        else:
            converted_target = bunch_target

        # Add names for any extra columns. We do not really check for duplicates because Pandas allow columns with the same name.
        for i in range(len(column_names), bunch_data.shape[1] + converted_target.shape[1]):
            column_names.append('column {i}'.format(i=i))

        data = pandas.concat([pandas.DataFrame(bunch_data), pandas.DataFrame(converted_target)], axis=1)
        data.columns = column_names
        data = container_pandas.DataFrame(data)

        # We do not update digest with new data generated here. This is OK because this data is determined by
        # original data so original digest still applies. When saving a new digest has to be computed anyway
        # because this data will have to be converted to string.
        data.insert(0, 'd3mIndex', range(len(data)))

        resources['learningData'] = data

        metadata = metadata.update(('learningData',), {
            'structural_type': type(data),
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/Table',
                'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint',
            ],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(data.columns),
            },
        })

        metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS, 0), {
            'name': 'd3mIndex',
            'structural_type': numpy.int64,
            'semantic_types': [
                'http://schema.org/Integer',
                'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
            ],
        })

        for column_index in range(1, bunch_data.shape[1] + 1):
            column_metadata: typing.Dict[str, typing.Any] = {
                'structural_type': bunch_data.dtype.type,
                'semantic_types': [
                    'https://metadata.datadrivendiscovery.org/types/UnknownType',
                    'https://metadata.datadrivendiscovery.org/types/Attribute',
                ],
                'name': data.columns[column_index],
            }

            metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS, column_index), column_metadata)

        for column_index in range(bunch_data.shape[1] + 1, bunch_data.shape[1] + bunch_target.shape[1] + 1):
            if target_values is not None:
                if len(target_values) == 2:
                    column_type = ['http://schema.org/Boolean']
                elif len(target_values) > 2:
                    column_type = ['https://metadata.datadrivendiscovery.org/types/CategoricalData']
                else:
                    raise exceptions.InvalidDatasetError("Too few target values in sklearn dataset.")
            else:
                column_type = ['https://metadata.datadrivendiscovery.org/types/UnknownType']

            column_metadata = {
                'structural_type': str if target_values is not None else bunch_target.dtype.type,
                'semantic_types': column_type + [
                    'https://metadata.datadrivendiscovery.org/types/SuggestedTarget',
                    'https://metadata.datadrivendiscovery.org/types/Attribute',
                ],
                'name': data.columns[column_index],
            }

            metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS, column_index), column_metadata)

        return metadata, bunch_description, bunch_digest

    def _get_digest(self, bunch: typing.Dict) -> str:
        hash = hashlib.sha256()

        hash.update(bunch['data'].tobytes())
        hash.update(bunch['target'].tobytes())

        if 'feature_names' in bunch:
            if isinstance(bunch['feature_names'], list):
                for feature_name in bunch['feature_names']:
                    hash.update(feature_name.encode('utf8'))
            else:
                hash.update(bunch['feature_names'].tobytes())

        if 'target_names' in bunch:
            if isinstance(bunch['target_names'], list):
                for target_name in bunch['target_names']:
                    hash.update(target_name.encode('utf8'))
            else:
                hash.update(bunch['target_names'].tobytes())

        if 'DESCR' in bunch:
            hash.update(bunch['DESCR'].encode('utf8'))

        return hash.hexdigest()

    def _get_bunch(self, dataset_path: str) -> typing.Dict:
        return getattr(datasets, 'load_{dataset_path}'.format(dataset_path=dataset_path))()

    # "strict_digest" is ignored, there is no metadata to compare digest against.
    # "handle_score_split is ignored as well.
    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, handle_score_split: bool = True) -> 'Dataset':
        assert self.can_load(dataset_uri)

        dataset_path = dataset_uri[len('sklearn://'):]

        if not hasattr(datasets, 'load_{dataset_path}'.format(dataset_path=dataset_path)):
            raise exceptions.DatasetNotFoundError("Sklearn dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri))

        dataset_description = None
        dataset_digest = None

        resources: typing.Dict = {}
        metadata = metadata_base.DataMetadata()

        if not lazy:
            load_lazy = None

            metadata, dataset_description, dataset_digest = self._load_data(
                resources, metadata, dataset_path=dataset_path, compute_digest=compute_digest,
            )

        else:
            def load_lazy(dataset: Dataset) -> None:
                # "dataset" can be used as "resources", it is a dict of values.
                dataset.metadata, dataset_description, dataset_digest = self._load_data(
                    dataset, dataset.metadata, dataset_path=dataset_path, compute_digest=compute_digest,
                )

                new_metadata: typing.Dict = {
                    'dimension': {'length': len(dataset)},
                }

                if dataset_description is not None:
                    new_metadata['description'] = dataset_description

                if dataset_digest is not None:
                    new_metadata['digest'] = dataset_digest

                dataset.metadata = dataset.metadata.update((), new_metadata)
                dataset.metadata = dataset.metadata.generate(dataset)

                dataset._load_lazy = None

        dataset_metadata = {
            'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or dataset_uri,
            'name': dataset_name or dataset_path,
            'location_uris': [
                dataset_uri,
            ],
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        if dataset_version is not None:
            dataset_metadata['version'] = dataset_version

        if dataset_description is not None:
            dataset_metadata['description'] = dataset_description

        if dataset_digest is not None:
            dataset_metadata['digest'] = dataset_digest

        metadata = metadata.update((), dataset_metadata)

        return Dataset(resources, metadata, load_lazy=load_lazy)


class D3MDatasetSaver(Saver):
    """
    A class for saving of D3M datasets.

    This saver supports only saving to local file system.
    URI should point to the ``datasetDoc.json`` file in the D3M dataset directory.
    """

    VERSION = '3.3.0'

    def can_save(self, dataset_uri: str) -> bool:
        if not self._is_dataset(dataset_uri):
            return False

        if not self._is_local_file(dataset_uri):
            return False

        return True

    def _is_dataset(self, uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(uri, allow_fragments=False)
        except Exception:
            return False

        if os.path.basename(parsed_uri.path) != 'datasetDoc.json':
            return False

        return True

    def _is_local_file(self, uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(uri, allow_fragments=False)
        except Exception:
            return False

        if parsed_uri.scheme != 'file':
            return False

        if parsed_uri.netloc not in ['', 'localhost']:
            return False

        if not parsed_uri.path.startswith('/'):
            return False

        return True

    def _get_column_description(self, column_index: int, column_metadata: typing.Dict) -> typing.Dict:
        column = {
            'colIndex': column_index,
            'colName': column_metadata['name'],
            'role': [SEMANTIC_TYPES_TO_D3M_ROLES[x] for x in column_metadata.get('semantic_types', []) if x in SEMANTIC_TYPES_TO_D3M_ROLES]
        }
        column_type = [SEMANTIC_TYPES_TO_D3M_COLUMN_TYPES[semantic_type] for semantic_type in column_metadata.get('semantic_types', []) if semantic_type in SEMANTIC_TYPES_TO_D3M_COLUMN_TYPES]

        # If column semantic_type is not specified we default to unknown type.
        if not column_type:
            if 'structural_type' in column_metadata:
                if utils.is_int(column_metadata['structural_type']):
                    column['colType'] = SEMANTIC_TYPES_TO_D3M_COLUMN_TYPES['http://schema.org/Integer']
                elif utils.is_float(column_metadata['structural_type']):
                    column['colType'] = SEMANTIC_TYPES_TO_D3M_COLUMN_TYPES['http://schema.org/Float']
                elif issubclass(column_metadata['structural_type'], bool):
                    column['colType'] = SEMANTIC_TYPES_TO_D3M_COLUMN_TYPES['http://schema.org/Boolean']
                else:
                    column['colType'] = SEMANTIC_TYPES_TO_D3M_COLUMN_TYPES['https://metadata.datadrivendiscovery.org/types/UnknownType']
            else:
                column['colType'] = SEMANTIC_TYPES_TO_D3M_COLUMN_TYPES['https://metadata.datadrivendiscovery.org/types/UnknownType']
        elif len(column_type) == 1:
            column['colType'] = column_type[0]
        else:
            raise exceptions.InvalidMetadataError(
                "More than one semantic type found for column type: {column_type}".format(
                    column_type=column_type,
                ),
            )

        if column_metadata.get('description', None):
            column['colDescription'] = column_metadata['description']

        return column

    def _get_collection_resource_description(self, dataset: 'Dataset', resource_id: str, resource: typing.Any, dataset_location_base_path: typing.Optional[str]) -> typing.Dict:
        if not isinstance(resource, container_pandas.DataFrame):
            raise exceptions.InvalidArgumentTypeError("Saving a D3M dataset with a collection resource which is not a DataFrame, but '{structural_type}'.".format(
                structural_type=type(resource),
            ))
        if len(resource.columns) != 1:
            raise exceptions.InvalidArgumentTypeError("Saving a D3M dataset with a collection resource with an invalid number of columns: {columns}".format(
                columns=len(resource.columns),
            ))
        if not dataset.metadata.has_semantic_type((resource_id, metadata_base.ALL_ELEMENTS, 0), 'https://metadata.datadrivendiscovery.org/types/FileName'):
            raise exceptions.InvalidArgumentTypeError("Saving a D3M dataset with a collection resource with with a column which does not contain filenames.")

        selector = (resource_id, metadata_base.ALL_ELEMENTS, 0)
        metadata, exceptions_with_selectors = dataset.metadata.query_with_exceptions(selector)

        # We check structural type for all rows in a column, but also if any row has a different structural type.
        for structural_type in [metadata['structural_type']] + [metadata['structural_type'] for metadata in exceptions_with_selectors.values() if 'structural_type' in metadata]:
            if not issubclass(structural_type, str):
                raise exceptions.InvalidArgumentTypeError("Saving a D3M dataset with a collection resource with with a column which does not just string values, but also '{structural_type}'.".format(
                    structural_type=structural_type,
                ))

        # We use "location_base_uris" from all rows. We only support "location_base_uris"
        # being the same for all rows, so we have to verify that.
        all_location_base_uris_nested = [
            list(metadata.get('location_base_uris', []))
        ] + [
            list(metadata['location_base_uris']) for metadata in exceptions_with_selectors.values() if 'location_base_uris' in metadata
        ]

        # Flatten the list of lists, remove duplicates, sort for reproducibility.
        all_location_base_uris = sorted({all_location_base_uri for all_location_base_uri in itertools.chain.from_iterable(all_location_base_uris_nested)})

        local_location_base_uris = [location_base_uri for location_base_uri in all_location_base_uris if self._is_local_file(location_base_uri)]

        if not local_location_base_uris:
            raise exceptions.NotSupportedError(
                "Saving a D3M dataset with a collection resource without local files is not supported: {all_location_base_uris}".format(
                    all_location_base_uris=all_location_base_uris,
                ),
            )
        elif len(local_location_base_uris) > 1:
            # When there are multiple base locations in D3M dataset format can lead to conflicts
            # where same filename in a column points to different files, but we are storing them
            # under the same resource path. We verify that there are no conflicts in "_save_collection".
            # Because there is no clear way to determine the best common resource path we use a hard-coded one.
            resource_path = 'files/'
        elif dataset_location_base_path is None:
            # We cannot determine the resource path so we use a hard-coded one.
            resource_path = 'files/'
        else:
            location_base_path = url_parse.urlparse(local_location_base_uris[0], allow_fragments=False).path

            # This is a way to check that "dataset_location_base_path" is a prefix of "location_base_path".
            if os.path.commonpath([location_base_path, dataset_location_base_path]) != dataset_location_base_path:
                raise exceptions.NotSupportedError(
                    "Saving a D3M dataset with a collection resource with files location not under the dataset directory.",
                )

            resource_path = location_base_path[len(dataset_location_base_path) + 1:]

        # Just a matter of style.
        if not resource_path.endswith('/'):
            resource_path += '/'

        resource_formats_set = set()
        # "media_types" for "ALL_ELEMENTS" is an union of all rows.
        for media_type in metadata.get('media_types', []):
            if media_type in MEDIA_TYPES_REVERSE:
                resource_formats_set.add(MEDIA_TYPES_REVERSE[media_type])
            else:
                # We allow unknown media types.
                resource_formats_set.add(media_type)

        resource_type = [SEMANTIC_TYPES_TO_D3M_RESOURCE_TYPES[semantic_type] for semantic_type in metadata.get('semantic_types', []) if semantic_type in SEMANTIC_TYPES_TO_D3M_RESOURCE_TYPES]

        if len(resource_type) != 1:
            raise exceptions.InvalidMetadataError(
                "Not exactly one semantic type found for resource type: {resource_type}".format(
                    resource_type=resource_type,
                ),
            )

        return {
            'resID': resource_id,
            'isCollection': True,
            # Sorting to have reproducibility.
            'resFormat': sorted(resource_formats_set),
            'resType': resource_type[0],
            'resPath': resource_path,
        }

    def _get_dataframe_resource_description(self, dataset: 'Dataset', resource_id: str, resource: typing.Any, dataset_location_base_path: typing.Optional[str]) -> typing.Dict:
        if dataset.metadata.has_semantic_type((resource_id,), 'https://metadata.datadrivendiscovery.org/types/EdgeList'):
            res_type = 'edgeList'
        else:
            res_type = 'table'

        resource_description = {
            'resID': resource_id,
            'isCollection': False,
            'resFormat': ['text/csv'],
            'resType': res_type,
        }

        if dataset.metadata.has_semantic_type((resource_id,), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint'):
            if resource_id != 'learningData':
                logger.error("Saving a dataset with a dataset entry point with resource ID not equal to 'learningData', but '%(resource_id)s'.", {'resource_id': resource_id})
            resource_description['resPath'] = 'tables/learningData.csv'
        else:
            resource_description['resPath'] = 'tables/{resource_id}.csv'.format(resource_id=resource_id)

        return resource_description

    # TODO: Make it easier to subclass to support other resource types.
    def _get_resource_description(self, dataset: 'Dataset', resource_id: str, resource: typing.Any, dataset_location_base_path: typing.Optional[str]) -> typing.Dict:
        if dataset.metadata.has_semantic_type((resource_id,), 'https://metadata.datadrivendiscovery.org/types/FilesCollection'):
            return self._get_collection_resource_description(dataset, resource_id, resource, dataset_location_base_path)

        elif isinstance(resource, container_pandas.DataFrame):
            return self._get_dataframe_resource_description(dataset, resource_id, resource, dataset_location_base_path)

        else:
            raise exceptions.NotSupportedError("Saving a D3M dataset with a resource with structural type '{structural_type}' is not supported.".format(structural_type=type(resource)))

    def _get_columns_description(self, dataset: 'Dataset', resource_id: str, resource: typing.Any) -> typing.List[typing.Dict]:
        columns = []

        # Traverse file columns in collections.
        if dataset.metadata.has_semantic_type((resource_id,), 'https://metadata.datadrivendiscovery.org/types/FilesCollection'):
            # We know there is only one column here. This has been verified in "_get_collection_resource_description".
            column_metadata = dataset.metadata.query((resource_id, metadata_base.ALL_ELEMENTS, 0))
            for file_column_index, file_column_metadata in enumerate(column_metadata.get('file_columns', [])):
                columns.append(self._get_column_description(file_column_index, file_column_metadata))

        # Traverse columns in a DataFrame.
        elif isinstance(resource, container_pandas.DataFrame):
            number_of_columns = len(resource.columns)
            for column_index in range(number_of_columns):
                column_selector = (resource_id, metadata_base.ALL_ELEMENTS, column_index)
                column_metadata = dataset.metadata.query(column_selector)

                column = self._get_column_description(column_index, column_metadata)

                if 'boundary_for' in column_metadata and 'foreign_key' in column_metadata:
                    raise exceptions.NotSupportedError("Both boundary and foreign key are not supported.")

                elif 'foreign_key' in column_metadata:
                    if column_metadata['foreign_key']['type'] == 'COLUMN':
                        refers_to = {
                            'resID': column_metadata['foreign_key']['resource_id'],
                            'resObject': {},
                        }

                        if 'column_name' in column_metadata['foreign_key']:
                            refers_to['resObject'] = {
                                'columnName': column_metadata['foreign_key']['column_name'],
                            }
                            referring_column_index = dataset.metadata.get_column_index_from_column_name(
                                column_metadata['foreign_key']['column_name'],
                                at=(column_metadata['foreign_key']['resource_id'],),
                            )
                        elif 'column_index' in column_metadata['foreign_key']:
                            refers_to['resObject'] = {
                                'columnIndex': column_metadata['foreign_key']['column_index'],
                            }
                            referring_column_index = column_metadata['foreign_key']['column_index']
                        else:
                            raise exceptions.InvalidMetadataError(f"\"foreign_key\" is missing a column reference, in metadata of column {column_index} of resource \"{resource_id}\".")

                        # A special case to handle a reference to a file collection.
                        if dataset.metadata.has_semantic_type(
                            (column_metadata['foreign_key']['resource_id'],),
                            'https://metadata.datadrivendiscovery.org/types/FilesCollection',
                        ) and dataset.metadata.has_semantic_type(
                            (column_metadata['foreign_key']['resource_id'], metadata_base.ALL_ELEMENTS, referring_column_index),
                            'https://metadata.datadrivendiscovery.org/types/FileName',
                        ):
                            refers_to['resObject'] = 'item'

                        column['refersTo'] = refers_to

                    elif column_metadata['foreign_key']['type'] in REFERENCE_MAP_REVERSE:
                        column['refersTo'] = {
                            'resID': column_metadata['foreign_key']['resource_id'],
                            'resObject': REFERENCE_MAP_REVERSE[column_metadata['foreign_key']['type']],
                        }

                elif 'boundary_for' in column_metadata:
                    refers_to = {
                        # "resource_id" is optional in our metadata and it
                        # means the reference is local to the resource.
                        'resID': column_metadata['boundary_for'].get('resource_id', resource_id),
                        'resObject': {},
                    }

                    if 'column_name' in column_metadata['boundary_for']:
                        refers_to['resObject'] = {
                            'columnName': column_metadata['boundary_for']['column_name'],
                        }
                    elif 'column_index' in column_metadata['boundary_for']:
                        refers_to['resObject'] = {
                            'columnIndex': column_metadata['boundary_for']['column_index'],
                        }
                    else:
                        raise exceptions.InvalidMetadataError(f"\"boundary_for\" is missing a column reference, in metadata of column {column_index} of resource \"{resource_id}\".")

                    column['refersTo'] = refers_to

                columns.append(column)

        return columns

    def _get_dataset_description(self, dataset: 'Dataset') -> typing.Dict:
        dataset_description: typing.Dict[str, typing.Any] = {
            'about': {
                'datasetSchemaVersion': self.VERSION,
            },
        }

        dataset_root_metadata = dataset.metadata.query(())

        for d3m_path, (dataset_path, required) in D3M_TO_DATASET_FIELDS.items():
            value = utils.get_dict_path(dataset_root_metadata, dataset_path)
            if value is not None:
                utils.set_dict_path(dataset_description, d3m_path, value)
            elif required:
                raise exceptions.InvalidMetadataError(f"Dataset metadata field {dataset_path} is required when saving.")

        for x in [dataset_root_metadata.get('stored_size', None), dataset_description['about'].get('approximateSize', None)]:
            if x is not None:
                exponent = int((math.log10(x) // 3) * 3)
                try:
                    unit = SIZE_TO_UNITS[exponent]
                except KeyError as error:
                    raise KeyError("Unit string for '{exponent}' not found in lookup dictionary {SIZE_TO_UNITS}.".format(exponent=exponent, SIZE_TO_UNITS=SIZE_TO_UNITS)) from error
                dataset_description['about']['approximateSize'] = str(x // (10 ** exponent)) + ' ' + unit
                break

        # We are only using the first URI due to design of D3M dataset format. Remaining URIs should be stored in qualities.
        if dataset_root_metadata.get('source', {}).get('uris', []):
            dataset_description['about']['sourceURI'] = dataset_root_metadata['source']['uris'][0]

        dataset_location_uris = [location_uri for location_uri in dataset_root_metadata.get('location_uris', []) if self._is_local_file(location_uri)]

        if dataset_location_uris:
            # If there are multiple local URIs, we pick the first.
            dataset_location_base_path = os.path.dirname(url_parse.urlparse(dataset_location_uris[0], allow_fragments=False).path)
        else:
            dataset_location_base_path = None

        data_resources = []

        for resource_id, resource in dataset.items():
            resource_description = self._get_resource_description(dataset, resource_id, resource, dataset_location_base_path)

            columns = self._get_columns_description(dataset, resource_id, resource)

            if columns:
                resource_description['columns'] = columns

            data_resources.append(resource_description)

        dataset_description['dataResources'] = data_resources

        return dataset_description

    def save(self, dataset: 'Dataset', dataset_uri: str, *, compute_digest: ComputeDigest = ComputeDigest.ALWAYS) -> None:
        assert self.can_save(dataset_uri)

        dataset_description = self._get_dataset_description(dataset)

        dataset_path = os.path.dirname(url_parse.urlparse(dataset_uri, allow_fragments=False).path)
        os.makedirs(dataset_path, 0o755, exist_ok=False)

        dataset_description_path = os.path.join(dataset_path, 'datasetDoc.json')

        # We use "x" mode to make sure file does not already exist.
        with open(dataset_description_path, 'x', encoding='utf8') as f:
            json.dump(dataset_description, f, indent=2, allow_nan=False)

        for resource_description in dataset_description['dataResources']:
            resource_id = resource_description['resID']
            resource = dataset[resource_id]

            self._save_resource(dataset, dataset_uri, dataset_path, resource_description, resource_id, resource)

        # We calculate digest of the new dataset and write it into datasetDoc.json
        dataset_description['about']['digest'] = get_d3m_dataset_digest(dataset_description_path)
        with open(dataset_description_path, 'w', encoding='utf8') as f:
            json.dump(dataset_description, f, indent=2, allow_nan=False)

        # TODO: Add saving of all other metadata which is not part of D3M schema as qualities.
        #       See: https://gitlab.com/datadrivendiscovery/d3m/issues/227

    # TODO: Make it easier to subclass to support non-local "location_base_uris".
    def _save_collection(self, dataset: 'Dataset', dataset_uri: str, dataset_path: str, resource_description: typing.Dict, resource_id: str, resource: typing.Any) -> None:
        # Here we can assume collection resource is a DataFrame which contains exactly one
        # column containing filenames. This has been verified in "_get_collection_resource_description".
        assert isinstance(resource, container_pandas.DataFrame), type(resource)
        assert len(resource.columns) == 1, resource.columns

        already_copied: typing.Set[typing.Tuple[str, str]] = set()
        linking_warning_issued = False

        for row_index, filename in enumerate(resource.iloc[:, 0]):
            # "location_base_uris" is required for collections.
            location_base_uris = dataset.metadata.query((resource_id, row_index, 0))['location_base_uris']

            local_location_base_uris = [location_base_uri for location_base_uri in location_base_uris if self._is_local_file(location_base_uri)]

            # We verified in "_get_collection_resource_description" that there is only one local URI.
            assert len(local_location_base_uris) == 1, local_location_base_uris
            local_location_base_uri = local_location_base_uris[0]

            # "location_base_uris" should be made so that we can just concat with the filename
            # ("location_base_uris" end with "/").
            source_uri = local_location_base_uri + filename
            source_path = url_parse.urlparse(source_uri, allow_fragments=False).path

            destination_path = os.path.join(dataset_path, resource_description['resPath'], filename)

            # Multiple rows can point to the same file, so we do not have to copy them multiple times.
            if (source_path, destination_path) in already_copied:
                continue

            os.makedirs(os.path.dirname(destination_path), 0o755, exist_ok=True)

            linked = False

            try:
                os.link(source_path, destination_path)
                linked = True

            except FileExistsError as error:
                # If existing file is the same, then this is OK. Multiple rows can point to the same file.
                if os.path.samefile(source_path, destination_path):
                    linked = True
                elif filecmp.cmp(source_path, destination_path, shallow=False):
                    linked = True
                # But otherwise we raise an exception.
                else:
                    raise exceptions.AlreadyExistsError(
                        "Destination file '{destination_path}' already exists with different content than '{source_path}' has.".format(
                            destination_path=destination_path,
                            source_path=source_path,
                        ),
                    ) from error

            except OSError as error:
                # OSError: [Errno 18] Invalid cross-device link
                if error.errno == errno.EXDEV:
                    pass
                else:
                    raise error

            # If we can't make a hard-link we try to copy the file.
            if not linked:
                if not linking_warning_issued:
                    linking_warning_issued = True
                    logger.warning("Saving dataset to '%(dataset_uri)s' cannot use hard-linking.", {'dataset_uri': dataset_uri})

                try:
                    with open(source_path, 'rb') as source_file:
                        with open(destination_path, 'xb') as destination_file:
                            shutil.copyfileobj(source_file, destination_file)

                except FileExistsError as error:
                    # If existing file is the same, then this is OK. Multiple rows can point to the same file.
                    if os.path.samefile(source_path, destination_path):
                        pass
                    elif filecmp.cmp(source_path, destination_path, shallow=False):
                        pass
                    # But otherwise we raise an exception.
                    else:
                        raise exceptions.AlreadyExistsError(
                            "Destination file '{destination_path}' already exists with different content than '{source_path}' has.".format(
                                destination_path=destination_path,
                                source_path=source_path,
                            ),
                        ) from error

            already_copied.add((source_path, destination_path))

    # TODO: Make it easier to subclass to support other column types.
    def _save_dataframe(self, dataset: 'Dataset', dataset_path: str, resource_description: typing.Dict, resource_id: str, resource: typing.Any) -> None:
        destination_path = os.path.join(dataset_path, resource_description['resPath'])
        # A subset of "simple_data_types".
        # TODO: Support additional types.
        #       Dicts we can try to convert to "json" column type. Lists of floats we can convert to "realVector".
        #       We could also probably support boolean values.
        supported_column_structural_types = (str, float, int, numpy.integer, numpy.float64, type(None))

        # We verify if structural types of columns are supported.
        for column_index in range(dataset.metadata.query((resource_id, metadata_base.ALL_ELEMENTS))['dimension']['length']):
            selector = (resource_id, metadata_base.ALL_ELEMENTS, column_index)
            metadata, exceptions_with_selectors = dataset.metadata.query_with_exceptions(selector)

            # We check structural type for all rows in a column, but also if any row has a different structural type.
            for structural_type in [metadata['structural_type']] + [metadata['structural_type'] for metadata in exceptions_with_selectors.values() if 'structural_type' in metadata]:
                if not issubclass(structural_type, supported_column_structural_types):
                    raise exceptions.NotSupportedError("Saving a D3M dataset with a column with structural type '{structural_type}' is not supported.".format(structural_type=structural_type))

        os.makedirs(os.path.dirname(destination_path), 0o755, exist_ok=True)

        # We use "x" mode to make sure file does not already exist.
        resource.to_csv(destination_path, mode='x', encoding='utf8')

    # TODO: Make it easier to subclass to support other resource types.
    def _save_resource(self, dataset: 'Dataset', dataset_uri: str, dataset_path: str, resource_description: typing.Dict, resource_id: str, resource: typing.Any) -> None:
        if resource_description.get('isCollection', False):
            self._save_collection(dataset, dataset_uri, dataset_path, resource_description, resource_id, resource)

        elif isinstance(resource, container_pandas.DataFrame):
            self._save_dataframe(dataset, dataset_path, resource_description, resource_id, resource)

        else:
            raise exceptions.NotSupportedError("Saving a D3M dataset with a resource with structural type '{structural_type}' is not supported.".format(structural_type=type(resource)))


D = typing.TypeVar('D', bound='Dataset')


# TODO: It should be probably immutable.
class Dataset(dict):
    """
    A class representing a dataset.

    Internally, it is a dictionary containing multiple resources (e.g., tables).

    Parameters
    ----------
    resources : Mapping
        A map from resource IDs to resources.
    metadata : DataMetadata
        Metadata associated with the ``data``.
    load_lazy : Callable
        If constructing a lazy dataset, calling this function will read all the
        data and convert the dataset to a non-lazy one.
    generate_metadata: bool
        Automatically generate and update the metadata.
    check : bool
        DEPRECATED: argument ignored.
    source : primitive or Any
        DEPRECATED: argument ignored.
    timestamp : datetime
        DEPRECATED: argument ignored.
    """

    metadata: metadata_base.DataMetadata = None
    loaders: typing.List[Loader] = [
        D3MDatasetLoader(),
        CSVLoader(),
        SklearnExampleLoader(),
    ]
    savers: typing.List[Saver] = [
        D3MDatasetSaver(),
    ]

    @deprecate.arguments('source', 'timestamp', 'check', message="argument ignored")
    def __init__(self, resources: typing.Mapping, metadata: metadata_base.DataMetadata = None, *,
                 load_lazy: typing.Callable[['Dataset'], None] = None, generate_metadata: bool = False,
                 check: bool = True, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        super().__init__(resources)

        if isinstance(resources, Dataset) and metadata is None:
            # We made a copy, so we do not have to generate metadata.
            self.metadata = resources.metadata
        elif metadata is not None:
            # We were provided metadata, so we do not have to generate metadata.
            self.metadata = metadata
        else:
            self.metadata = metadata_base.DataMetadata()
            if generate_metadata:
                self.metadata = self.metadata.generate(self)

        self._load_lazy = load_lazy

    @classmethod
    def load(cls, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, handle_score_split: bool = True) -> 'Dataset':
        """
        Tries to load dataset from ``dataset_uri`` using all registered dataset loaders.

        Parameters
        ----------
        dataset_uri : str
            A URI to load.
        dataset_id : str
            Override dataset ID determined by the loader.
        dataset_version : str
            Override dataset version determined by the loader.
        dataset_name : str
            Override dataset name determined by the loader.
        lazy : bool
            If ``True``, load only top-level metadata and not whole dataset.
        compute_digest : ComputeDigest
            Compute a digest over the data?
        strict_digest : bool
            If computed digest does not match the one provided in metadata, raise an exception?
        handle_score_split : bool
            If a scoring dataset has target values in a separate file, merge them in?

        Returns
        -------
        Dataset
            A loaded dataset.
        """

        for loader in cls.loaders:
            if loader.can_load(dataset_uri):
                return loader.load(
                    dataset_uri, dataset_id=dataset_id, dataset_version=dataset_version, dataset_name=dataset_name,
                    lazy=lazy, compute_digest=compute_digest, strict_digest=strict_digest, handle_score_split=handle_score_split,
                )

        raise exceptions.DatasetUriNotSupportedError(
            "No known loader could load dataset from '{dataset_uri}'.".format(dataset_uri=dataset_uri),
        )

    def save(self, dataset_uri: str, *, compute_digest: ComputeDigest = ComputeDigest.ALWAYS) -> None:
        """
        Tries to save dataset to ``dataset_uri`` using all registered dataset savers.

        Parameters
        ----------
        dataset_uri : str
            A URI to save to.
        compute_digest : ComputeDigest
            Compute digest over the data when saving?
        """

        for saver in self.savers:
            if saver.can_save(dataset_uri):
                saver.save(self, dataset_uri, compute_digest=compute_digest)
                return

        raise exceptions.DatasetUriNotSupportedError("No known saver could save dataset to '{dataset_uri}'.".format(dataset_uri=dataset_uri))

    def is_lazy(self) -> bool:
        """
        Return whether this dataset instance is lazy and not all data has been loaded.

        Returns
        -------
        bool
            ``True`` if this dataset instance is lazy.
        """

        return self._load_lazy is not None

    def load_lazy(self) -> None:
        """
        Read all the data and convert the dataset to a non-lazy one.
        """

        if self._load_lazy is not None:
            self._load_lazy(self)

    # TODO: Allow one to specify priority which would then insert loader at a different place and not at the end?
    @classmethod
    def register_loader(cls, loader: Loader) -> None:
        """
        Registers a new dataset loader.

        Parameters
        ----------
        loader : Loader
            An instance of the loader class implementing a new loader.
        """

        cls.loaders.append(loader)

    # TODO: Allow one to specify priority which would then insert saver at a different place and not at the end?
    @classmethod
    def register_saver(cls, saver: Saver) -> None:
        """
        Registers a new dataset saver.

        Parameters
        ----------
        saver : Saver
            An instance of the saver class implementing a new saver.
        """

        cls.savers.append(saver)

    def __repr__(self) -> str:
        return self.__str__()

    def _get_description_keys(self) -> typing.Sequence[str]:
        return 'id', 'name', 'location_uris'

    def __str__(self) -> str:
        metadata = self.metadata.query(())

        return '{class_name}({description})'.format(
            class_name=type(self).__name__,
            description=', '.join('{key}=\'{value}\''.format(key=key, value=metadata[key]) for key in self._get_description_keys() if key in metadata),
        )

    def copy(self: D) -> D:
        # Metadata is copied from provided iterable.
        return type(self)(resources=self, load_lazy=self._load_lazy)

    def __copy__(self: D) -> D:
        return self.copy()

    def select_rows(self: D, row_indices_to_keep: typing.Mapping[str, typing.Sequence[int]]) -> D:
        """
        Generate a new Dataset from the row indices for DataFrames.

        Parameters
        ----------
        row_indices_to_keep : Mapping[str, Sequence[int]]
            This is a dict where key is resource ID and value is a sequence of row indices to keep.
            If a resource ID is missing, the whole related resource is kept.

        Returns
        -------
        Dataset
            Returns a new Dataset.
        """

        resources = {}
        metadata = self.metadata

        for resource_id, resource in self.items():
            # We keep any resource which is missing from "row_indices_to_keep".
            if resource_id not in row_indices_to_keep:
                resources[resource_id] = resource
            else:
                if not isinstance(resource, container_pandas.DataFrame):
                    raise exceptions.InvalidArgumentTypeError("Only DataFrame resources can have rows selected, not '{type}'.".format(type=type(resource)))

                row_indices = sorted(row_indices_to_keep[resource_id])
                resources[resource_id] = self[resource_id].iloc[row_indices, :].reset_index(drop=True)

                # TODO: Expose this as a general metadata method.
                #       In that case this has to be done recursively over all nested ALL_ELEMENTS.
                #       Here we are operating at resource level so we have to iterate only over first
                #       ALL_ELEMENTS and resource's element itself.

                # Change the metadata. Update the number of rows in the split.
                # This makes a copy so that we can modify metadata in-place.
                metadata = metadata.update(
                    (resource_id,),
                    {
                        'dimension': {
                            'length': len(row_indices),
                        },
                    },
                )

                # Remove all rows not in this split and reorder those which are.
                for element_metadata_entry in [
                    metadata._current_metadata.all_elements,
                    metadata._current_metadata.elements[resource_id],
                ]:
                    if element_metadata_entry is None:
                        continue

                    elements = element_metadata_entry.elements
                    new_elements_evolver = utils.EMPTY_PMAP.evolver()
                    for i, row_index in enumerate(row_indices):
                        if row_index in elements:
                            new_elements_evolver.set(i, elements[row_index])
                    element_metadata_entry.elements = new_elements_evolver.persistent()
                    element_metadata_entry.is_elements_empty = not element_metadata_entry.elements
                    element_metadata_entry.update_is_empty()

        return type(self)(resources, metadata)

    def get_relations_graph(self) -> typing.Dict[str, typing.List[typing.Tuple[str, bool, int, int, typing.Dict]]]:
        """
        Builds the relations graph for the dataset.

        Each key in the output corresponds to a resource/table. The value under a key is the list of
        edges this table has. The edge is represented by a tuple of four elements. For example,
        if the edge is ``(resource_id, True, index_1, index_2, custom_state)``, it
        means that there is a foreign key that points to table ``resource_id``. Specifically,
        ``index_1`` column in the current table points to ``index_2`` column in the table ``resource_id``.

        ``custom_state`` is an empty dict when returned from this method, but allows users
        of this graph to store custom state there.

        Returns
        -------
        Dict[str, List[Tuple[str, bool, int, int, Dict]]]
            Returns the relation graph in adjacency representation.
        """

        graph: typing.Dict[str, typing.List[typing.Tuple[str, bool, int, int, typing.Dict]]] = collections.defaultdict(list)

        for resource_id in self.keys():
            if not issubclass(self.metadata.query((resource_id,))['structural_type'], container_pandas.DataFrame):
                continue

            columns_length = self.metadata.query((resource_id, metadata_base.ALL_ELEMENTS,))['dimension']['length']
            for index in range(columns_length):
                column_metadata = self.metadata.query((resource_id, metadata_base.ALL_ELEMENTS, index))

                if 'foreign_key' not in column_metadata:
                    continue

                if column_metadata['foreign_key']['type'] != 'COLUMN':
                    continue

                foreign_resource_id = column_metadata['foreign_key']['resource_id']

                # "COLUMN" foreign keys should not point to non-DataFrame resources.
                assert isinstance(self[foreign_resource_id], container_pandas.DataFrame), type(self[foreign_resource_id])

                if 'column_index' in column_metadata['foreign_key']:
                    foreign_index = column_metadata['foreign_key']['column_index']
                elif 'column_name' in column_metadata['foreign_key']:
                    foreign_index = self.metadata.get_column_index_from_column_name(column_metadata['foreign_key']['column_name'], at=(foreign_resource_id,))
                else:
                    raise exceptions.UnexpectedValueError("Invalid foreign key: {foreign_key}".format(foreign_key=column_metadata['foreign_key']))

                # "True" and "False" implies forward and backward relationships, respectively.
                graph[resource_id].append((foreign_resource_id, True, index, foreign_index, {}))
                graph[foreign_resource_id].append((resource_id, False, foreign_index, index, {}))

        return graph

    def get_column_references_by_column_index(self) -> typing.Dict[str, typing.Dict[metadata_base.ColumnReference, typing.List[metadata_base.ColumnReference]]]:
        references: typing.Dict[str, typing.Dict[metadata_base.ColumnReference, typing.List[metadata_base.ColumnReference]]] = {
            'confidence_for': {},
            'boundary_for': {},
            'foreign_key': {},
        }

        for resource_id, resource in self.items():
            if not isinstance(resource, container_pandas.DataFrame):
                continue

            resource_references = self.metadata.get_column_references_by_column_index(resource_id, at=(resource_id,))

            references['confidence_for'].update(resource_references['confidence_for'])
            references['boundary_for'].update(resource_references['boundary_for'])
            references['foreign_key'].update(resource_references['foreign_key'])

        return references

    @classmethod
    def _canonical_dataset_description(cls, dataset_description: typing.Dict) -> typing.Dict:
        """
        Currently, this is just removing any local URIs the description might have.
        """

        # Making a copy.
        dataset_description = dict(dataset_description)

        utils.filter_local_location_uris(dataset_description)

        return dataset_description

    def to_json_structure(self, *, canonical: bool = False) -> typing.Dict:
        """
        Returns only a top-level dataset description.
        """

        dataset_description = utils.to_json_structure(self.metadata.query(()))

        if canonical:
            dataset_description = self._canonical_dataset_description(dataset_description)

        metadata_base.CONTAINER_SCHEMA_VALIDATOR.validate(dataset_description)

        return dataset_description


def dataset_serializer(obj: Dataset) -> dict:
    data = {
        'metadata': obj.metadata,
        'dataset': dict(obj),
    }

    if type(obj) is not Dataset:
        data['type'] = type(obj)

    return data


def dataset_deserializer(data: dict) -> Dataset:
    dataset = data.get('type', Dataset)(data['dataset'], data['metadata'])
    return dataset


if pyarrow_lib is not None:
    pyarrow_lib._default_serialization_context.register_type(
        Dataset, 'd3m.dataset',
        custom_serializer=dataset_serializer,
        custom_deserializer=dataset_deserializer,
    )


def get_dataset(dataset_uri: str, *, compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, lazy: bool = False) -> Dataset:
    dataset_uri = utils.fix_uri(dataset_uri)

    return Dataset.load(dataset_uri, compute_digest=compute_digest, strict_digest=strict_digest, lazy=lazy)


def describe_handler(arguments: argparse.Namespace, *, dataset_resolver: typing.Callable = None) -> None:
    if dataset_resolver is None:
        dataset_resolver = get_dataset

    has_errored = False

    for dataset_path in arguments.datasets:
        if getattr(arguments, 'list', False):
            print(dataset_path)

        try:
            start_timestamp = time.perf_counter()
            dataset = dataset_resolver(
                dataset_path,
                compute_digest=ComputeDigest[getattr(arguments, 'compute_digest', ComputeDigest.ONLY_IF_MISSING.name)],
                strict_digest=getattr(arguments, 'strict_digest', False),
                lazy=getattr(arguments, 'lazy', False),
            )
            end_timestamp = time.perf_counter()
        except Exception as error:
            if getattr(arguments, 'continue', False):
                traceback.print_exc(file=sys.stdout)
                print(f"Error loading dataset: {dataset_path}")
                has_errored = True
                continue
            else:
                raise Exception(f"Error loading dataset: {dataset_path}") from error

        try:
            if getattr(arguments, 'print', False) or getattr(arguments, 'metadata', False) or getattr(arguments, 'time', False):
                if getattr(arguments, 'print', False):
                    pprint.pprint(dataset)
                if getattr(arguments, 'metadata', False):
                    dataset.metadata.pretty_print()
                if getattr(arguments, 'time', False):
                    print(f"Time: {(end_timestamp - start_timestamp):.3f}s")
            else:
                dataset_description = dataset.to_json_structure(canonical=True)

                json.dump(
                    dataset_description,
                    sys.stdout,
                    indent=(getattr(arguments, 'indent', 2) or None),
                    sort_keys=getattr(arguments, 'sort_keys', False),
                    allow_nan=False,
                )  # type: ignore
                sys.stdout.write('\n')
        except Exception as error:
            if getattr(arguments, 'continue', False):
                traceback.print_exc(file=sys.stdout)
                print(f"Error describing dataset: {dataset_path}")
                has_errored = True
                continue
            else:
                raise Exception(f"Error describing dataset: {dataset_path}") from error

    if has_errored:
        sys.exit(1)


def convert_handler(arguments: argparse.Namespace, *, dataset_resolver: typing.Callable = None) -> None:
    if dataset_resolver is None:
        dataset_resolver = get_dataset

    try:
        dataset = dataset_resolver(
            arguments.input_uri,
            compute_digest=ComputeDigest[getattr(arguments, 'compute_digest', ComputeDigest.ONLY_IF_MISSING.name)],
            strict_digest=getattr(arguments, 'strict_digest', False),
        )
    except Exception as error:
        raise Exception(f"Error loading dataset '{arguments.input_uri}'.") from error

    output_uri = utils.fix_uri(arguments.output_uri)

    try:
        dataset.save(output_uri)
    except Exception as error:
        raise Exception(f"Error saving dataset '{arguments.input_uri}' to '{output_uri}'.") from error


def main(argv: typing.Sequence) -> None:
    raise exceptions.NotSupportedError("This CLI has been removed. Use \"python3 -m d3m dataset describe\" instead.")


if __name__ == '__main__':
    main(sys.argv)
