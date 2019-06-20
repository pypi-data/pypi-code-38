import os
import typing
import pandas

from d3m import container, utils as d3m_utils
from d3m.metadata import base as metadata_base, hyperparams
from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase
from d3m.primitive_interfaces.base import CallResult

import common_primitives
from common_primitives import utils

from sri.common import config

Inputs = container.Dataset
Outputs = container.Dataset

class Hyperparams(hyperparams.Hyperparams):
    dataframe_resource = hyperparams.Hyperparameter[typing.Union[str, None]](
        default=None,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="If there are multiple resources inside a Dataset, which one to extract?",
    )
    use_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of column indices to force primitive to operate on. If any specified column does not contain text filenames, it is skipped.",
    )
    exclude_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of column indices to not operate on. Applicable only if \"use_columns\" is not provided.",
    )


class DatasetTextReader(TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """
This primitive accepts a dataset with columns of file names containing textual data, and replaces each such
column with one containing the string contents of the corresponding files, returning a dataset.

It offers the following hyperparameters:

* **dataframe_resource**: The key of the dataset resource on which to operate.  If None is provided (default),
  the primitive operates on the resource with the semantic type DatasetEntryPoint.
* **use_columns**: A set of column indexes on which to operate.  Default is an empty set, in which case all
  suitable columns will be selected.  A column is suitable if it has semantic type FileName with media type
  text/plain.  The primitive will not process any columns deemed unsuitable, whatever is specified by this
  hyperparameter.
* **exclude_columns**: A set of column indexes on which not to operate.  Tested only if use_columns is empty.
    """

    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': '005941a3-e3ca-49d9-9e99-4f5566831acd',
            'version': config.VERSION,
            'name': 'Columns text reader',
            'python_path': 'd3m.primitives.data_preprocessing.dataset_text_reader.DatasetTextReader',
            'keywords': ['text', 'reader'],
            'source': config.SOURCE,
            'installation': [ config.INSTALLATION ],
            'algorithm_types': [
                metadata_base.PrimitiveAlgorithmType.FILE_MANIPULATION,
            ],
            'supported_media_types': [
                'text/plain'
            ],
            'primitive_family': metadata_base.PrimitiveFamily.DATA_PREPROCESSING,
        }
    )


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        rid = self._get_resource_id(inputs)
        use_cols = self._get_columns(inputs, rid, self.hyperparams)
        if len(use_cols) == 0:
            return CallResult(inputs)
        outputs = inputs.copy()
        metadata = outputs.metadata
        resource = outputs[rid]
        ALLELTS = metadata_base.ALL_ELEMENTS
        for ci in use_cols:
            newcol, mdata = self._produce_column(outputs, rid, ci) 
            resource.iloc[:, ci] = newcol
            metadata = metadata.update((rid, ALLELTS, ci), mdata, source=self)
#            new_metadata = newframe.metadata._current_metadata.all_elements.elements[0]
#            metadata._current_metadata.elements[rid].all_elements.elements[new_column_index] = new_metadata
#            metadata = utils.copy_metadata(newframe.metadata, metadata, (ALLELTS, 0), (rid, ALLELTS, new_column_index))
#            metadata = metadata.update((rid, ALLELTS), 
#                                       dict(dimension=dict(length=new_column_index+1)))
#            newcol.metadata = mdata
#            resource = utils.append_columns(resource, newcol)
        outputs[rid] = resource
        outputs.metadata = metadata
        return CallResult(outputs)


    def _get_resource_id(self, inputs):
        use_rid = self.hyperparams['dataframe_resource']
        entry_type = 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint'
        if use_rid is None:
            for rid in inputs.keys():
                if entry_type in inputs.metadata.query((rid,)).get('semantic_types', []):
                    use_rid = rid
        if use_rid is None:
            raise ValueError("Unable to find starting resource")
        return use_rid


    def _get_columns(self, inputs: Inputs, rid: str, hyperparams: Hyperparams) -> typing.List[int]:
        columns = list(hyperparams['use_columns'])
        exclude = list(hyperparams['exclude_columns'])
        if len(columns) == 0:
            mdata = inputs.metadata.query((rid, metadata_base.ALL_ELEMENTS))
            width = mdata['dimension']['length']
            columns = [ ci for ci in range(width) if not ci in exclude ]
        columns = [ ci for ci in columns if self._can_use_column(inputs, rid, ci)]
        return columns


    def _can_use_column(self, inputs, rid, column_index):
        column_metadata = inputs.metadata.query((rid, metadata_base.ALL_ELEMENTS, column_index))

        if self._column_property(inputs, rid, column_index, 'structural_type') != str:
            return False
        try:
            foreign_resource_id, foreign_column = self._get_foreign_key(inputs, rid, column_index)
        except (KeyError, ValueError):
            return False

        semantic_types = self._column_property(inputs, foreign_resource_id, foreign_column, 'semantic_types', [])
        if 'https://metadata.datadrivendiscovery.org/types/FileName' not in semantic_types:
            return False;

        media_types = self._column_property(inputs, foreign_resource_id, foreign_column, 'media_types', [])
        if 'text/plain' not in media_types:
            return False

        return True


    def _produce_column(self, inputs, rid, column_index):
        fres, fcol = self._get_foreign_key(inputs, rid, column_index)
        base_uri = self._column_property(inputs, fres, fcol, 'location_base_uris')[0]
        if base_uri.startswith('file://'):
            path = base_uri[7:]
        else:
            raise NotImplementedError("Non-file URIs not currently supported")
        
        def _get_contents(fname):
            with open(path + fname, "r") as fh:
                return fh.read()

        newdata = [ _get_contents(f) for f in inputs[fres].iloc[:,fcol] ]
#        df = container.DataFrame(newdata, generate_metadata=True)
        column_metadata = self._produce_column_metadata(
            inputs.metadata, rid, column_index, self)
#        df.metadata = df.metadata.update((metadata_base.ALL_ELEMENTS, 0), column_metadata)
        return newdata, column_metadata


    def _produce_column_metadata(self, inputs_metadata, rid, ci, source):
        query = (rid, metadata_base.ALL_ELEMENTS, ci)
        mdata = dict(inputs_metadata.query(query))
        mdata['structural_type'] = str
        mdata['location_base_uris'] = metadata_base.NO_VALUE
        mdata['media_types'] = metadata_base.NO_VALUE
        mdata['foreign_key'] = metadata_base.NO_VALUE
        stypes = [ t for t in mdata['semantic_types'] 
                   if t != 'https://metadata.datadrivendiscovery.org/types/FileName' ]
        if 'http://schema.org/Text' not in stypes:
            stypes.append('http://schema.org/Text')
        mdata['semantic_types'] = stypes
        return mdata
#        return metadata_base.Metadata(mdata)


    def _get_foreign_key(self, inputs, rid, ci):
        foreign_key = self._column_property(inputs, rid, ci, 'foreign_key')
        if foreign_key is None:
            raise KeyError("No foreign_key")
        foreign_type = foreign_key['type']
        if foreign_type != 'COLUMN':
            raise ValueError("Foreign reference must be to column")
        foreign_resource_id = foreign_key['resource_id']
        foreign_column = foreign_key['column_index']
        return foreign_resource_id, foreign_column


    def _column_property(self, inputs, rid, ci, prop, default=None):
        query = (rid, metadata_base.ALL_ELEMENTS, ci)
        return inputs.metadata.query(query)[prop]
