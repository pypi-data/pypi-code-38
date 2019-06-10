# Copyright (c) Microsoft Corporation. All rights reserved.
"""Builders module contains builder classes that could be used to create various transformation steps in interactive manner.
"""

from .engineapi.typedefinitions import (FieldInference, DataSourceProperties,
                                        AnonymousDataSourceProseSuggestionsMessageArguments, FileEncoding,
                                        BlockArguments, AddBlockToListMessageArguments, PropertyValues,
                                        ColumnsSelector, StaticColumnsSelectorDetails, ColumnsSelectorType,
                                        SingleColumnSelectorDetails, AnonymousSendMessageToBlockMessageArguments,
                                        ColumnsSelectorDetails, SplitFillStrategyConstraint, FieldType,
                                        ReplaceValueFunction, StringMissingReplacementOption, JoinType,
                                        JoinSuggestionResult, SummaryFunction)

from .engineapi.api import EngineAPI
from .datasources import FileDataSource
from .references import make_activity_reference
from .errorhandlers import PandasImportError
from ._pandas_helper import have_pandas
from .typeconversions import (CandidateConverter, CandidateDateTimeConverter, InferenceInfo,
                              get_converters_from_candidates)
from .parseproperties import (parse_properties_from_datasource_properties, ParseDatasourceProperties,
                              ParseDelimitedProperties, ParseFixedWidthProperties, ParseLinesProperties,
                              ParseParquetProperties, ReadExcelProperties, ReadJsonProperties)
from .step import Step, steps_to_block_datas, step_to_block_data
from .types import SplitExample, Delimiters
from ... import dataprep
import json
from typing import List, Dict, cast, Any, TypeVar, Optional, Tuple
from copy import deepcopy
from textwrap import dedent
import datetime


# noinspection PyUnresolvedReferences
def _to_pandas_dataframe(data: Any) -> 'pandas.DataFrame':
    if not have_pandas():
        raise PandasImportError()
    else:
        import pandas
    return pandas.DataFrame(data)


class InferenceArguments:
    """
    Class to control data type inference behavior.

    :param day_first: If set to True, inference will choose date formats where day comes before month.
    :type day_first: bool
    """
    def __init__(self, day_first: bool):
        self.day_first = day_first


class ColumnTypesBuilder:
    """
    Interactive object that can be used to infer column types and type conversion attributes.
    """
    def __init__(self, dataflow: 'dataprep.Dataflow', engine_api: EngineAPI):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._conversion_candidates = {}

    def _run_type_inference(self, steps: List[Step]) -> Dict[str, InferenceInfo]:
        def _type_converter_from_inference_result(result: FieldInference) -> CandidateConverter:
            if result.type == FieldType.DATE:
                conversion_arguments = result.arguments
                datetime_formats = cast(List[str], conversion_arguments['datetimeFormats'])
                ambiguous_formats = cast(List[List[str]], conversion_arguments['ambiguousFormats'])
                return CandidateDateTimeConverter(datetime_formats, ambiguous_formats)
            else:
                return CandidateConverter(result.type)

        def _inference_info_from_result(result: FieldInference) -> InferenceInfo:
            return InferenceInfo([_type_converter_from_inference_result(result)])

        inferences = self._engine_api.infer_types(steps_to_block_datas(steps))
        return {col: _inference_info_from_result(inference) for col, inference in inferences.items()}

    @property
    def conversion_candidates(self) -> Dict[str, InferenceInfo]:
        """
        Current dictionary of conversion candidates, where key is column name and value is list of conversion candidates.

        .. remarks::

            The values in the conversion_candidates dictionary could be of several types:

            * :class:`azureml.dataprep.InferenceInfo` (wraps a List of :class:`azureml.dataprep.CandidateConverter`) - populated based on available data by running :meth:`learn`.
            * :class:`azureml.dataprep.FieldType` - user override to force conversion to a specific type.
            * :class:`azureml.dataprep.TypeConverter` - another way to perform a user override to force conversion to a specific type.
            * Tuple of :class:`azureml.dataprep.FieldType`.DATE and List of format strings (single format string is also supported) - user override for date conversions.

            .. code-block:: python

                import azureml.dataprep as dprep

                dataflow = dprep.read_csv(path='./some/path')
                builder = dataflow.builders.set_column_types()
                builder.conversion_candidates['MyNumericColumn'] = dprep.FieldType.DECIMAL    # force conversion to decimal
                builder.conversion_candidates['MyBoolColumn'] = dprep.FieldType.BOOLEAN       # force conversion to bool
                builder.conversion_candidates['MyDateColumnWithFormat'] = (dprep.FieldType.DATE, ['%m-%d-%Y'])  # force conversion to date with month before day
                builder.conversion_candidates['MyOtherDateColumn'] = dprep.DateTimeConverter(['%d-%m-%Y'])      # force conversion to data with day before month (alternative way)

            .. note::

                This will be populated automatically with inferred conversion candidates when :meth:`learn` is called.
                Any modifications made to this dictionary will be discarded any time :meth:`learn` is called.

        """
        return self._conversion_candidates

    @property
    def ambiguous_date_columns(self) -> List[str]:
        """
        List of columns, where ambiguous date formats were detected.

        .. remarks::

            Each of the ambiguous date columns must be resolved before calling :meth:`to_dataflow`. There are 3 ways to resolve
                ambiguity:

            * Override the value for the column in :func:`azureml.dataprep.api.builders.ColumnTypesBuilder.conversion_candidates` dictionary with a desired date conversion format.
            * Drop conversions for the ambiguous date columns by calling :func:`azureml.dataprep.api.builders.ColumnTypesBuilder.ambiguous_date_conversions_drop`
            * Resolve date conversion ambiguity for all columns by calling :func:`azureml.dataprep.api.builders.ColumnTypesBuilder.ambiguous_date_conversions_keep_day_month`
                or :func:`azureml.dataprep.api.builders.ColumnTypesBuilder.ambiguous_date_conversions_keep_month_day`

        :return: List of columns, where ambiguous date formats were detected.
        """
        if not self._conversion_candidates:
            return []
        result = []
        for col, inference_result in self._conversion_candidates.items():
            if not isinstance(inference_result, InferenceInfo):
                # user has overridden inference info, don't check it here
                continue
            date_converters = \
                (c for c in inference_result.candidate_converters if isinstance(c, CandidateDateTimeConverter))
            for candidate in date_converters:
                if candidate.ambiguous_formats is not None and len(candidate.ambiguous_formats) > 0:
                    result.append(col)
                    break

        return result

    def ambiguous_date_conversions_drop(self) -> None:
        """
        Resolves ambiguous date conversion candidates by removing them from the conversion dictionary.

        .. note::

            Resolving ambiguity this way will ensure that such columns remain unchanged.
        """
        if not self._conversion_candidates:
            return
        columns_to_skip = self.ambiguous_date_columns
        for col in columns_to_skip:
            del self._conversion_candidates[col]

    def _resolve_date_ambiguity(self, prefer_day_first: bool):
        if not self._conversion_candidates:
            return
        for col, inference_result in self._conversion_candidates.items():
            date_converters = \
                (c for c in inference_result.candidate_converters if isinstance(c, CandidateDateTimeConverter))
            for candidate in date_converters:
                candidate.resolve_ambiguity(prefer_day_first)

    def ambiguous_date_conversions_keep_day_month(self) -> None:
        """
        Resolves ambiguous date conversion candidates by only keeping date formats where day comes before month.
        """
        self._resolve_date_ambiguity(True)

    def ambiguous_date_conversions_keep_month_day(self) -> None:
        """
        Resolves ambiguous date conversion candidates by only keeping date formats where month comes before day.
        """
        self._resolve_date_ambiguity(False)

    def learn(self, inference_arguments: InferenceArguments = None) -> None:
        """
        Performs a pull on the data and populates :func:`ColumnTypesBuilder.conversion_candidates` with automatically inferred conversion candidates for each column.

        :param inference_arguments: (Optional) Argument that would force automatic date format ambiguity resolution for all columns.
        """
        if inference_arguments is not None and not isinstance(inference_arguments, InferenceArguments):
            raise ValueError('Unexpected inference arguments. Expected instance of InferenceArguments class')
        self._conversion_candidates = self._run_type_inference(self._dataflow._get_steps())
        if inference_arguments is not None:
            self._resolve_date_ambiguity(inference_arguments.day_first)

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Uses current state of this object to add 'set_column_types' step to the original Dataflow.

        .. note::

            This call will fail if there are any unresolved date format ambiguities remaining.

        :return: The modified Dataflow.
        """
        if self._conversion_candidates == {}:
            self.learn()
        if len(self.ambiguous_date_columns) > 0:
            raise ValueError('Please resolve date conversion ambiguity in column(s): ' + str(self.ambiguous_date_columns))
        candidates = {col: info.candidate_converters if isinstance(info, InferenceInfo) else info
                      for col, info in self._conversion_candidates.items()}
        converters = get_converters_from_candidates(candidates)
        return self._dataflow.set_column_types(converters)

    def __repr__(self):
        return """Column types conversion candidates:
""" + ',\n'.join(["""{0!r}: {1!r}""".format(col, converters) for col, converters in self.conversion_candidates.items()])


class FileFormatArguments:
    """
    Defines and stores the arguments which can affect learning on a 'FileFormatBuilder'.
    """

    def __init__(self, all_files: bool):
        """
        :param all_files: Specifies whether learning will occur on all files (True) or just the first one (False).
        """
        self.all_files = all_files


class FileFormatBuilder:
    """
    Interactive object that can learn the file format and properties required to read a given file.

    .. remarks::

        This Builder is generally used on a Dataflow which has had a 'get_files' step applied to it. After the path(s)
            to files have been resolved, the appropriate method of interpreting those files can be learned and modified
            using this Builder.

    :var file_format: Result of file format detection.
    """

    def __init__(self, dataflow: 'dataprep.Dataflow', engine_api: EngineAPI):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self.file_format = {}  # type: ParseDatasourceProperties

    def _run_prose_file_detection(self) -> DataSourceProperties:
        msg_args = AnonymousDataSourceProseSuggestionsMessageArguments(
            blocks=steps_to_block_datas(self._dataflow._get_steps()))
        return self._engine_api.anonymous_data_source_prose_suggestions(msg_args)

    def learn(self, fileformat_arguments: FileFormatArguments = None) -> None:
        """
        Learn the `file_format` of the files from the initial Dataflow.

        .. remarks::

            After calling this function the 'file_format' attribute on this Builder will be populated with
                information about the file(s) in the initial Dataflow. This attribute includes file type as well
                as some parameters to be used when parsing the file(s).

        :param fileformat_arguments: (Optional) FileFormatArguments to use.
        """
        fileformat_arguments = fileformat_arguments or FileFormatArguments(False)
        if fileformat_arguments.all_files:
            raise NotImplementedError("Currently only learning from the first file is supported.")
        datasource_properties = self._run_prose_file_detection()
        self.file_format = parse_properties_from_datasource_properties(datasource_properties)

        # if file format is json, further learning is required so delegate to specific builder
        if type(self.file_format) == ReadJsonProperties and self.file_format.json_extract_program == '':
            builder = self._dataflow.builders.extract_table_from_json(encoding=self.file_format.encoding)
            builder.learn()
            self.file_format.json_extract_program = builder.json_extract_program

    def to_dataflow(self, include_path: bool = False) -> 'dataprep.Dataflow':
        """
        Uses learned information about the files in the initial Dataflow to construct a new Dataflow
            which has the correct reading/parsing steps to extract their data.

        :param include_path: (Optional) Whether to include a column containing the path from which the data was read.
        :return: A new Dataflow with the appropriate parsing/reading steps applied based on the learned information.
        """
        if self.file_format == {}:
            self.learn()
        if type(self.file_format) == ParseDelimitedProperties:
            dflow = self._dataflow.parse_delimited(**vars(self.file_format))
        elif type(self.file_format) == ParseFixedWidthProperties:
            dflow = self._dataflow.parse_fwf(**vars(self.file_format))
        elif type(self.file_format) == ParseLinesProperties:
            dflow = self._dataflow.parse_lines(**vars(self.file_format))
        elif type(self.file_format) == ParseParquetProperties:
            dflow = self._dataflow.read_parquet_file()
        elif type(self.file_format) == ReadExcelProperties:
            dflow = self._dataflow.read_excel(**vars(self.file_format))
        elif type(self.file_format) == ReadJsonProperties:
            dflow = self._dataflow.read_json(**vars(self.file_format))
        else:
            raise RuntimeError("Unsupported datasource type.")
        if not include_path:
            dflow = dflow.drop_columns(['Path'])
        return dflow


class JsonTableBuilder:
    """
    Interactive object that can learn program for table extraction from json document.

    .. remarks::

        This Builder is generally used on a Dataflow which has had a 'get_files' step applied to it. After the path(s)
            to files have been resolved, if files are json files, a program to extract data into tabular form can be learned
            using this Builder.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 flatten_nested_arrays: bool = False,
                 encoding: FileEncoding = FileEncoding.UTF8):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._read_json_args = BlockArguments(block_type='JSONFile')  # type: BlockArguments
        self._arguments = {
            'dsl': '',
            'flattenNestedArrays': flatten_nested_arrays,
            'fileEncoding': encoding}  # type: Dict[str, Any]
        self._read_json_step = None
        self._dirty = False

    @property
    def flatten_nested_arrays(self) -> bool:
        """
        Property controlling program's handling of nested arrays.

        .. remarks::

            If set to False, then a json object like this:
            `{a: { b: 'value', c: [1, 2, 3] }}`
            will result in:
            | a.b   |    a.c    |
            | value | [1, 2, 3] |

            If set to True, then the result will become:
            | a.b   |    a.c    |
            | value | 1         |
            | value | 2         |
            | value | 3         |

            .. note::

                Setting this to True could result in significantly larger number of rows generated by the program.
        """
        return self._arguments['flattenNestedArrays']

    @flatten_nested_arrays.setter
    def flatten_nested_arrays(self, value: bool):
        self._dirty = True
        self._arguments['flattenNestedArrays'] = value

    @property
    def encoding(self) -> FileEncoding:
        """
        Encoding used to read json file.
        """
        return self._arguments['fileEncoding']

    @encoding.setter
    def encoding(self, value: FileEncoding):
        self._dirty = True
        self._arguments['fileEncoding'] = value

    @property
    def json_extract_program(self) -> str:
        """
        Inspect learned program. If this is not None, then program was learned.
        """
        return self._read_json_step.arguments.to_pod()['dsl'] if self._read_json_step is not None else None

    def learn(self) -> None:
        """
        Learn table extraction program based on the json file structure.

        .. remarks::

            After calling this function the :func:`JsonTableBuilder.json_extract_program` will be populated with a serialized
                program string (if a program could be generated). Otherwise it will be None.
        """
        preceding_blocks = steps_to_block_datas(self._dataflow._get_steps())
        self._read_json_args.arguments = PropertyValues.from_pod(self._arguments)
        self._dirty = False
        self._read_json_step = self._engine_api.add_block_to_list(
            AddBlockToListMessageArguments(new_block_arguments=self._read_json_args,
                                           blocks=preceding_blocks))
        args = self._read_json_step.arguments.to_pod()
        if args['dsl'] is None or len(args['dsl']) == 0:
            raise ValueError("Can't extract table from this JSON file")

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Uses learned information about structure of json files in the initial Dataflow to construct a new Dataflow
            with tabular representation of the data from those files.

        :return: A new Dataflow with data in tabular form.
        """
        args = self._read_json_step.arguments.to_pod()
        if self._read_json_step is None or self._dirty or args['dsl'] is None or len(args['dsl']) == 0:
            self.learn()

        return self._dataflow.read_json(json_extract_program=args['dsl'],
                                        encoding=args['fileEncoding'])


# noinspection PyUnresolvedReferences
SourceData = TypeVar('SourceData', Dict[str, str], 'pandas.Series')


class DeriveColumnByExampleBuilder:
    """
    Interactive object that can be used to learn program for deriving a column based on a set of source columns and
        examples.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 source_columns: List[str],
                 new_column_name: str):
        self._new_column_name = new_column_name
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._derive_column_args = BlockArguments(
            block_type='Microsoft.DPrep.DeriveColumnByExample')  # type: BlockArguments
        self._source_columns = source_columns
        self._arguments = {
            'dsl': '',
            'priorColumnIds': ColumnsSelector(type=ColumnsSelectorType.STATICLIST,
                                              details=cast(ColumnsSelectorDetails,
                                                           StaticColumnsSelectorDetails(source_columns))),
            'columnId': new_column_name,
            'anchorColumnId': source_columns[-1]}  # type: Dict[str, Any]
        self._derive_column_step = None
        self._dirty = False
        self._examples = []

    def _ensure_learn(self):
        args = self._derive_column_step.arguments.to_pod() if self._derive_column_step is not None else None
        if args is None or self._dirty or args['dsl'] is None or len(args['dsl']) == 0:
            self.learn()

    def learn(self) -> None:
        """
        Learn program that adds a new column in which values satisfy constrain set by source data and examples provided.

        .. remarks::

            Calling this function will trigger an attempt to generate a program that satisfies all the provided constraints (examples).
        """
        preceding_blocks = steps_to_block_datas(self._dataflow._get_steps())
        examples_dict = {example['row']: example for example in self._examples}
        self._arguments['examples'] = json.dumps(examples_dict)
        self._arguments['dsl'] = ''
        self._dirty = False
        self._derive_column_args.arguments = PropertyValues.from_pod(self._arguments)
        self._derive_column_step = self._engine_api.add_block_to_list(
            AddBlockToListMessageArguments(new_block_arguments=self._derive_column_args,
                                           blocks=preceding_blocks))
        args = self._derive_column_step.arguments.to_pod()
        if args['dsl'] is None or len(args['dsl']) == 0:
            raise ValueError("Can't derive column. Check provided examples.")

    # noinspection PyUnresolvedReferences
    def preview(self, skip: int = 0, count: int = 10) -> 'pandas.DataFrame':
        """
        Preview result of the generated program.

        .. remarks::

            Returned DataFrame consists of all the source columns used by the program as well as the derived column.

        :param skip: Number of rows to skip. Allows you to move preview window forward. Default is 0.
        :param count: Number of rows to preview. Default is 10.
        :return: pandas.DataFrame with preview data.
        :rtype: pandas.DataFrame
        """
        self._ensure_learn()
        args = self._derive_column_step.arguments.to_pod()
        return self._dataflow \
            .keep_columns(self._source_columns) \
            .add_step('Microsoft.DPrep.DeriveColumnByExample', args) \
            .skip(skip) \
            .head(count)

    def add_example(self, source_data: SourceData, example_value: str) -> None:
        """
        Adds an example value that will be used when learning a program to derive the new column.

        .. remarks::

            If an identical example is already present, this will do nothing.
            If a conflicting example is given (identical source_data but different example_value), an exception
                will be raised.

        :param source_data: Source data for the provided example.
            Generally should be a Dict[str, str] or pandas.Series where key of dictionary or index of series are column
            names and values are corresponding column values.
            Easiest way to provide source_data is to pass in a specific row of pandas.DataFrame (eg. df.iloc[2])

        :param example_value: Desired result for the provided source data.
        """

        # verify that source_data has all the required keys
        for required_column in self._source_columns:
            if required_column not in source_data:
                raise ValueError('Missing required source_data for column ' + required_column)

        # check if example with the same source_data was already added and raise in case of conflicting example
        min_example_id = 0
        for example_item in self._examples:
            current_id = example_item['row']
            min_example_id = min_example_id if min_example_id < current_id else current_id
            current_source_data = example_item['sourceData']
            duplicate = all(current_source_data[c] == source_data[c] for c in current_source_data)
            if duplicate:
                if example_value == example_item['example']:
                    # exactly same example found, do nothing
                    return
                else:
                    raise ValueError('Detected conflicting example. Another example with the same source_data but'
                                     ' different example_value already exists. Existing example_id is: '
                                     + str(current_id))
        self._dirty = True
        # handle case where there are some row based examples and this is the first synthetic one
        next_example_id = min_example_id - 1
        self._examples.append({
            'row': next_example_id,
            'sourceData': {key: source_data[key] if key in source_data else None for key in self._source_columns},
            'example': example_value})

    # noinspection PyUnresolvedReferences
    def list_examples(self) -> 'pandas.DataFrame':
        """
        Gets examples that are currently used to generate a program to derive a column.

        :return: pandas.DataFrame with examples.
        :rtype: pandas.DataFrame
        """
        list_of_examples = [{'example_id': example_item['row'],
                             **{k: v for k, v in example_item['sourceData'].items()},
                             'example': example_item['example']} for example_item in self._examples]
        return _to_pandas_dataframe(list_of_examples)

    # noinspection PyUnresolvedReferences
    def delete_example(self, example_id: int = None, example_row: 'pandas.Series' = None):
        """
        Deletes example, so it's no longer considered in program generation.

        .. note::

            Can be used with either full example row from list_examples() result or just example_id.

        :param example_id: Id of example to delete.
        :param example_row: Example row to delete.
        """
        example_id = example_id if example_id is not None else example_row['example_id']

        try:
            self._examples = [ex for ex in self._examples if ex['row'] != example_id]
            self._dirty = True
        except KeyError:
            pass

    # noinspection PyUnresolvedReferences
    def generate_suggested_examples(self) -> 'pandas.DataFrame':
        """
        List examples that, if provided, would improve confidence in the generated program.

        .. note::

            This operation will internally make a pull on the data in order to generate suggestions.

        :return: pandas.DataFrame of suggested examples.
        :rtype: pandas.DataFrame
        """
        self._ensure_learn()
        blocks = steps_to_block_datas(self._dataflow._get_steps())
        blocks.append(self._derive_column_step)
        response = self._engine_api.anonymous_send_message_to_block(
            AnonymousSendMessageToBlockMessageArguments(blocks=blocks,
                                                        message='getSuggestedInputs',
                                                        message_arguments=None)).to_pod()
        list_of_suggestions = [si['input']['sourceData'] for si in response['data']['significantInputs']]
        return _to_pandas_dataframe(list_of_suggestions)

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Uses the program learned based on the provided examples to derive a new column and create a new dataflow.

        :return: A new Dataflow with a derived column.
        """
        self._ensure_learn()
        args = self._derive_column_step.arguments.to_pod()
        return self._dataflow.add_step('Microsoft.DPrep.DeriveColumnByExample', args)

    def __repr__(self):
        return dedent("""\
            DeriveColumnByExampleBuilder
                source_columns: {0!r}
                new_column_name: '{1!s}'
                example_count: {2!s}
                has_program: {3!s}
            """.format(self._source_columns, self._new_column_name, len(self._examples),
                       self._arguments['dsl'] is not None))


class OneHotEncodingBuilder:
    """
    Interactive object that can be used to generate one hot encoding columns.

    .. remarks::

        This builder allows for generation, modification and preview of categorical labels used to create one hot encoding columns.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 source_column: str,
                 prefix: str):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._column = source_column
        self._arguments = {
            'column': ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN,
                                      details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(source_column))),
            'categoricalLabels': None,
            'prefix': prefix
        }

    def __repr__(self):
        return dedent("""\
            OneHotEncodingBuilder
                source_column: '{0!s}'
                categorical_labels: {1!r},
                prefix: '{2!s}'
            """.format(self._column, self._arguments['categoricalLabels'], self._arguments['prefix']))

    def learn(self) -> None:
        """
        Generates categorical labels.

        .. note::

            This operation will internally make a pull on the data.
        """
        blocks = steps_to_block_datas(self._dataflow._get_steps())
        one_hot_encoding_block = self._engine_api.add_block_to_list(
            AddBlockToListMessageArguments(blocks=blocks,
                                           new_block_arguments=BlockArguments(self._arguments, 'Microsoft.DPrep.OneHotEncodingBlock')))
        learned_arguments = one_hot_encoding_block.arguments.to_pod()
        result = learned_arguments['categoricalLabels']
        if result is None or len(result) == 0:
            raise ValueError('Failed to get categorical labels. '
                             'The current upper limit for labels is 1000 distinct values.')
        self._arguments['categoricalLabels'] = result

    @property
    def categorical_labels(self) -> List[str]:
        """
        Returns a list of strings representing the categorical labels.

        .. remarks::

            This can be assigned by calling :func:`azureml.dataprep.api.builders.OneHotEncodingBuilder.learn`, which will generate and set the labels for you.
            Alternatively, you can directly assign the value to categorical_labels.
        """
        return self._arguments['categoricalLabels']

    @categorical_labels.setter
    def categorical_labels(self, value):
        self._arguments['categoricalLabels'] = value

    @property
    def prefix(self) -> str:
        """
        String to append to new column names produced by one_hot_encode.

        .. remarks::

            If no prefix is provided, source column name will be used as one (e.g. <source_column>_label1, <source_column>_label2, ...).
        """
        return self._arguments.get('prefix')

    @prefix.setter
    def prefix(self, value):
        self._arguments['prefix'] = value

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Returns a new dataflow that contains a new binary column for each categorical label.

        .. remarks::

            If no categorical labels are explicitly defined, they are learned from the values in the source column.

        :return: A new dataflow with one hot encoded columns.
        """
        if self._arguments.get('categoricalLabels') is None or len(self._arguments['categoricalLabels']) == 0:
            self.learn()

        return self._dataflow.add_step('Microsoft.DPrep.OneHotEncodingBlock', self._arguments)


class LabelEncoderBuilder:
    """
    Interactive object that can be used to generate encoded labels.

    .. remarks::

        This Builder allows for generation, modification and preview of encoded labels.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 source_column: str,
                 new_column_name:str):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._column = source_column
        self._encoded_labels = {}
        self._arguments = {
            'column': ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN,
                                      details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(source_column))),
            'newColumnId': new_column_name,
            'encodedLabelsMap': None
        }

    def __repr__(self):
        return dedent("""\
            LabelEncoderBuilder
                source_column: '{0!s}'
                new_column_name: '{1!s}'
                encoded_labels: {2!r}
            """.format(self._column, self._arguments['newColumnId'], self._encoded_labels))

    def learn(self) -> None:
        """
        Generates encoded labels from source_column's values.
        """
        blocks = steps_to_block_datas(self._dataflow._get_steps())
        label_encoder_block = self._engine_api.add_block_to_list(
            AddBlockToListMessageArguments(blocks=blocks,
                                           new_block_arguments=BlockArguments(self._arguments, 'Microsoft.DPrep.LabelEncoderBlock')))
        learned_arguments = label_encoder_block.arguments.to_pod()
        encoded_labels_map = learned_arguments['encodedLabelsMap']

        if encoded_labels_map is None or len(encoded_labels_map) == 0:
            raise ValueError('Failed to get encoded labels. The current upper limit for labels is 10000 distinct values.')
        self._arguments['encodedLabelsMap'] = encoded_labels_map

    @property
    def encoded_labels(self) -> Dict[str, int]:
        """
        Returns a dictionary of encoded labels.

        .. remarks::

            `encoded_labels` can be assigned by calling :meth:`learn`, which will generate and assign the labels for you.
            Alternatively, you can directly assign the value to encoded_labels.
        """
        return { encoded_label['valueToLabel']: encoded_label['encodedLabel'] for encoded_label in self._arguments['encodedLabelsMap'] }

    @encoded_labels.setter
    def encoded_labels(self, value):
        self._encoded_labels = value
        self._arguments['encodedLabelsMap'] = [
            {'valueToLabel': key, 'encodedLabel': val} for key, val in self._encoded_labels.items()
        ]

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Returns a new dataflow with encoded labels in a new column. If encoded_labels are not defined, they will be learned from source_column's values.

        :return: A new Dataflow with a new column that contains encoded labels.
        """
        if self._arguments.get('encodedLabelsMap') is None or len(self._arguments['encodedLabelsMap']) == 0:
            self.learn()

        return self._dataflow.add_step('Microsoft.DPrep.LabelEncoderBlock', self._arguments)


class PivotBuilder:
    """
    Interactive object that can be used to generate pivoted columns from the selected pivot columns.

    .. remarks::

        This Builder allows for generation, modification and preview of pivoted columns.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 columns_to_pivot: List[str],
                 value_column: str,
                 summary_function: SummaryFunction = None,
                 group_by_columns: List[str] = None,
                 null_value_replacement: str = None,
                 error_value_replacement: str = None):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._columns_to_pivot = columns_to_pivot
        self._value_column = value_column
        self._summary_function = summary_function
        self._group_by_columns = group_by_columns
        self._null_value_replacement = null_value_replacement
        self._error_value_replacement = error_value_replacement
        self._pivoted_columns = None
        self._block_arguments = {
            'columnsToPivot': ColumnsSelector(type=ColumnsSelectorType.STATICLIST,
                                            details=cast(ColumnsSelectorDetails, StaticColumnsSelectorDetails(self._columns_to_pivot))),
            'valueColumn': ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN,
                                          details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(self._value_column))),
            'pivotedColumns': self._pivoted_columns,
            'summaryFunction': self._summary_function,
            'groupByColumns': self._group_by_columns,
            'nullValueReplacement': self._null_value_replacement,
            'errorValueReplacement': self._error_value_replacement
        }

    def __repr__(self):
        return dedent("""\
            PivotBuilder
                columns_to_pivot: '{0!s}',
                value_column: '{1!s}',
                summary_function: '{2!s}',
                group_by_columns: '{3!s}',
                pivoted_columns: '{4!s}',
                null_value_replacement: '{5!s}',
                error_value_replacement: '{6!s}'
            """.format(self._columns_to_pivot,
                       self._value_column,
                       self._summary_function,
                       self._group_by_columns,
                       self._pivoted_columns,
                       self._null_value_replacement,
                       self._error_value_replacement))

    def learn(self) -> None:
        """
        Generates pivoted columns from selected pivot columns values. There will be one pivoted column generated per distinct row, where each distinct row is defined
            by the values in the selected pivot columns.
        """
        self._block_arguments['pivotedColumns'] = None
        df = self._dataflow.add_step('Microsoft.DPrep.PivotBlock', self._block_arguments)
        blocks = steps_to_block_datas(df._get_steps())
        response = self._engine_api.anonymous_send_message_to_block(
            AnonymousSendMessageToBlockMessageArguments(blocks=blocks,
                                                        message='getPivotedColumns',
                                                        message_arguments=None)).to_pod()
        pivoted_columns = response['data']['pivotedColumns']
        if pivoted_columns is None or len(pivoted_columns) == 0:
            raise ValueError('Could not generate pivoted_columns from pivot columns selected.')
        self._pivoted_columns = pivoted_columns
        self._block_arguments['pivotedColumns'] = pivoted_columns

    @property
    def pivoted_columns(self) -> List[str]:
        """
        Returns the list of pivoted columns.

        .. remarks::

            pivoted_columns can be assigned by calling :meth:`learn`, which will generate and assign the pivoted_columns for you.
            Alternatively, you can directly assign the value to pivoted_columns.
        """
        return self._block_arguments['pivotedColumns']

    @pivoted_columns.setter
    def pivoted_columns(self, value) -> List[str]:
        self._pivoted_columns = value
        self._block_arguments['pivotedColumns'] = value

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Returns a new dataflow with encoded labels in a new column. If encoded_labels are not defined, they will be learned from source_column's values.

        :return: A new Dataflow with a new column that contains encoded labels.
        """
        if self._block_arguments.get('pivotedColumns') is None or len(self._block_arguments['pivotedColumns']) == 0:
            self.learn()

        return self._dataflow.add_step('Microsoft.DPrep.PivotBlock', self._block_arguments)





class MinMaxScalerBuilder:
    """
    Interactive object that can be used to min-max scale a column.

    .. remarks::

        This Builder allows for getting the min/max of the data, and the customization of all arguments to the scaler.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 column: str,
                 range_min: float,
                 range_max: float,
                 data_min: float,
                 data_max: float):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._column = column
        self._range_min = range_min
        self._range_max = range_max
        self._data_min = data_min
        self._data_max = data_max
        self._arguments = {
            'column': ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN,
                                      details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(column))),
            'rangeMin': self._range_min,
            'rangeMax': self._range_max,
            'dataMin': self._data_min,
            'dataMax': self._data_max
        }

    def __repr__(self):
        return dedent("""\
            MinMaxScalerBuilder
                column: '{0!s}'
                range_min: {1!s}
                range_max: {2!s}
                data_min: {3!s}
                data_max: {4!s}
            """.format(self._column, self._range_min, self._range_max, self._data_min, self._data_max))

    def learn(self) -> None:
        """
        Scan data to determine min and max of data and save them as arguments on the scaler builder.

        .. remarks::

            After calling this function, data_min and data_max will be populated with the results from the data scan.
            If data_min and/or data_max are not provided (i.e. None), they will be replaced by results from the data scan.
            All arguments on this builder (range_min, range_max, data_min, data_max) can be manually set.
        """
        if self._data_min is None or self._data_max is None:
            blocks = steps_to_block_datas(self._dataflow._get_steps())
            min_max_scaler_block = self._engine_api.add_block_to_list(
                AddBlockToListMessageArguments(blocks=blocks,
                                               new_block_arguments=BlockArguments(self._arguments, 'Microsoft.DPrep.MinMaxScalerBlock')))
            learned_arguments = min_max_scaler_block.arguments.to_pod()

            if "dataMin" in learned_arguments:
                self._data_min = learned_arguments['dataMin']
                self._arguments['dataMin'] = self._data_min
            if "dataMax" in learned_arguments:
                self._data_max = learned_arguments['dataMax']
                self._arguments['dataMax'] = self._data_max

            if self._data_min is None:
                if self._data_max is None:
                    raise ValueError('Failed to retrieve data_min and data_max.')
                raise ValueError('Failed to retrieve data_min.')
            if self._data_max is None:
                raise ValueError('Failed to retrieve data_max.')

        self._validate_data_range()

    def _validate_data_range(self) -> None:
        if self._data_min >= self._data_max:
            raise ValueError('Invalid data range [{0}, {1}]: data_min must be less than data_max.'
                             .format(self._data_min, self._data_max))

    def _validate_range(self) -> None:
        if self._range_min >= self._range_max:
            raise ValueError('Invalid range [{0}, {1}]: range_min must be less than range_max.'
                             .format(self._range_min, self._range_max))

    @property
    def range_min(self) -> float:
        return self._range_min

    @range_min.setter
    def range_min(self, value):
        self._range_min = value
        self._arguments['rangeMin'] = value

    @property
    def range_max(self) -> float:
        return self._range_max

    @range_max.setter
    def range_max(self, value):
        self._range_max = value
        self._arguments['rangeMax'] = value

    @property
    def data_min(self) -> float:
        return self._data_min

    @data_min.setter
    def data_min(self, value):
        self._data_min = value
        self._arguments['dataMin'] = value

    @property
    def data_max(self) -> float:
        return self._data_max

    @data_max.setter
    def data_max(self, value):
        self._data_max = value
        self._arguments['dataMax'] = value

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Returns a new dataflow with the specified column min-max scaled.

        :return: A new Dataflow with min-max scaled column.
        """
        self.learn()
        self._validate_range()
        return self._dataflow.add_step('Microsoft.DPrep.MinMaxScalerBlock', self._arguments)


class FuzzyGroupBuilder:
    """
    Interactive object that can be used to `FuzzyGroup` similar values to their canonical form.

    .. remarks::

        This Builder allows for generation, modification and preview of FuzzyGroups.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 source_column: str,
                 new_column_name: str,
                 similarity_threshold: float,
                 similarity_score_column_name: str):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._source_column = source_column
        self._new_column_name = new_column_name
        self._similarity_score_column_name = similarity_score_column_name
        add_sim_column = len(similarity_score_column_name) > 0 if similarity_score_column_name is not None else False
        self._arguments = {
            'groups': None,
            'column': ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN,
                                      details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(source_column))),
            'canonicalValueColumnName': new_column_name,
            'similarityScoreColumnName': similarity_score_column_name,
            'addSimilarityScoreColumn': add_sim_column}  # type: Dict[str, Any]
        self.similarity_threshold = similarity_threshold

    def learn(self) -> None:
        """
        Scans the data in the 'source_column' and generates groups of similar values.

        .. remarks::

            If successful, results of this function could be inspected via :meth:`groups` property of this Builder.
        """
        df = self._dataflow.add_step('Microsoft.DPrep.ClusterTextBlock', self._arguments)
        blocks = steps_to_block_datas(df._get_steps())
        response = self._engine_api.anonymous_send_message_to_block(
            AnonymousSendMessageToBlockMessageArguments(blocks,
                                                        'generateClusters',
                                                        {'similarityThreshold': self._arguments['similarityThreshold']})).to_pod()
        groups = response['data']['results']
        if groups is None or len(groups) == 0:
            raise ValueError('No groups were detected, try changing similarity_threshold and calling learn() again')
        self._arguments['groups'] = groups

    @property
    def groups(self) -> List[Dict[str, Any]]:
        """
        Returns a copy of a List of groups detected in the source_column.

        .. remarks::

            This list can be inspected, mutated and then assigned back to this property to achieve desired results.

            Each group is a Dict where:
            -'canonicalValue': contains the desired value to normalize all group entries to.
            -'duplicates': contains a List of Dicts, where each entry has:
            --'duplicateValue': value that will be replaced by 'canonicalValue'
            --'similarityScore': this score is calculated when groups are detected
            --'useForReplacement': has to be True for this value to be replaced with 'canonicalValue'
        """
        groups_value = self._arguments.get('groups')
        if groups_value is None or len(groups_value) == 0:
            self.learn()
        return deepcopy(self._arguments['groups'])

    @groups.setter
    def groups(self, value):
        if value is None or not isinstance(value, List):
            raise ValueError('Invalid groups value. List expected')
        found_duplicates = []
        # Validate incoming groups
        for group in value:
            if not isinstance(group, Dict) or 'canonicalValue' not in group or 'duplicates' not in group:
                raise ValueError('Unexpected group object. Group has to have canonicalValue and duplicates properties')
            duplicates = group['duplicates']
            if not isinstance(duplicates, List):
                raise ValueError('Unexpected duplicates value. duplicates has to be a list')
            for duplicate in duplicates:
                if not isinstance(duplicate, Dict) \
                        or 'duplicateValue' not in duplicate \
                        or 'similarityScore' not in duplicate \
                        or 'useForReplacement' not in duplicate:
                    raise ValueError('Unexpected duplicate object. Duplicate object has to have duplicateValue,'
                                     ' similarityScore and useForReplacement properties')
                if duplicate['duplicateValue'] in found_duplicates:
                    raise ValueError('duplicateValues have to be unique across all groups. Found repeated value: ' +
                                     duplicate['duplicateValue'])
                found_duplicates.append(duplicate['duplicateValue'])

        self._arguments['groups'] = value

    @property
    def similarity_threshold(self) -> float:
        """
        Controls how similar values should be to be grouped. It will be used during the next learn() call.

        .. note::

            Valid range is (0-1], where 1 is identical (case insensitive).
        """
        return self._arguments['similarityThreshold']

    @similarity_threshold.setter
    def similarity_threshold(self, value: float):
        if value <= 0 or value > 1:
            raise ValueError('Invalid value for similarity_threshold. Valid range (0-1]')
        self._arguments['similarityThreshold'] = float(value)

    @property
    def new_column_name(self) -> float:
        """
        Name of the newly added column with canonicalized values.
        """
        return self._arguments['canonicalValueColumnName']

    @new_column_name.setter
    def new_column_name(self, value: str):
        self._arguments['canonicalValueColumnName'] = value

    @property
    def similarity_score_column_name(self) -> float:
        """
        Name of the column with similarity scores for each replacement.

        .. note::

            If no name is provided, column with similarity score won't be added.
            Values in similarity_score_column are only present when original value was replaced with canonical.
        """
        return self._arguments['similarityScoreColumnName']

    @similarity_score_column_name.setter
    def similarity_score_column_name(self, value: str):
        self._arguments['similarityScoreColumnName'] = value
        add_sim_column = False if value is None else len(value) > 0
        self._arguments['addSimilarityScoreColumn'] = add_sim_column

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Adds fuzzy_group step to the current dataflow.

        :return: A new Dataflow with a FuzzyGrouped column and (optionally) similarity score column.
        """
        if self._arguments['groups'] is None or len(self._arguments['groups']) == 0:
            self.learn()

        return self._dataflow.add_step('Microsoft.DPrep.ClusterTextBlock', self._arguments)


class SplitColumnByExampleBuilder:
    """
    Interactive object that can be used to learn program for splitting a column based into a set of columns based on
        provided examples.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 source_column: str,
                 keep_delimiters: bool = False,
                 delimiters: List[str] = None):
        delimiters = delimiters or []
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._split_column_args = BlockArguments(
            block_type='Microsoft.DPrep.SplitColumnByExampleBlock')  # type: BlockArguments
        self._source_column = source_column
        self._arguments = {
            'dsl': '',
            'column': ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN,
                                      details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(source_column))),
            'keepDelimiter': keep_delimiters,
            'delimiters': delimiters,
            'fillStrategy': SplitFillStrategyConstraint.NONE}
        self._split_column_step = None
        self._dirty = False
        self._examples = []

    @property
    def delimiters(self) -> List[str]:
        """
        One of the options for generating a split program is to provide a list of delimiters that should be used.

        :return: If delimiters were provided, returns them.
        """
        return self._arguments['delimiters']

    @delimiters.setter
    def delimiters(self, delimiters: Delimiters):
        """
        Sets the delimiters to be used for split program generation.

        .. note::

            This will clear all examples.

        :param delimiters: A single string or List of strings that should be treated as split delimiters.
        """
        if isinstance(delimiters, str):
            delimiters = [delimiters]
        self._arguments['delimiters'] = delimiters
        self._examples = []
        self._dirty = True

    @property
    def keep_delimiters(self) -> bool:
        """Controls whether columns with delimiters should be kept in resulting data."""
        return self._arguments['keepDelimiter']

    @keep_delimiters.setter
    def keep_delimiters(self, keep_delimiters: bool):
        self._arguments['keepDelimiter'] = keep_delimiters
        self._examples = []
        self._dirty = True

    def _ensure_learn(self):
        args = self._split_column_step.arguments.to_pod() if self._split_column_step is not None else None
        if args is None or self._dirty or args['dsl'] is None or len(args['dsl']) == 0:
            self.learn()

    def learn(self) -> None:
        """
        Learn program that splits source_column into multiple columns based on delimiters or examples provided.

        .. remarks::

            After calling this function an attempt will be made to generate a program that satisfies all the provided constraints.
            Raises ValueError if the program can't be generated.
        """
        preceding_blocks = steps_to_block_datas(self._dataflow._get_steps())
        examples = [{'input': item[0], 'output': item[1]} for item in self._examples]
        self._arguments['examples'] = json.dumps(examples)
        self._arguments['dsl'] = ''
        self._dirty = False
        self._split_column_args.arguments = PropertyValues.from_pod(self._arguments)
        self._split_column_step = self._engine_api.add_block_to_list(
            AddBlockToListMessageArguments(new_block_arguments=self._split_column_args,
                                           blocks=preceding_blocks))
        args = self._split_column_step.arguments.to_pod()
        if args['dsl'] is None or len(args['dsl']) == 0:
            raise ValueError("Can't split column. Provide or update examples.")

    # noinspection PyUnresolvedReferences
    def preview(self, skip: int = 0, count: int = 10) -> 'pandas.DataFrame':
        """
        Preview result of the generated program.

        .. remarks::

            Returned DataFrame consists of the source column used by the program and all generated splits.

        :param skip: Number of rows to skip. Allows you to move preview window forward. Default is 0.
        :param count: Number of rows to preview. Default is 10.
        :return: pandas.DataFrame with preview data.
        :rtype: pandas.DataFrame
        """
        self._ensure_learn()
        args = self._split_column_step.arguments.to_pod()
        return self._dataflow \
            .keep_columns(self._source_column) \
            .add_step('Microsoft.DPrep.SplitColumnByExampleBlock', args) \
            .skip(skip) \
            .head(count)

    def add_example(self, example: SplitExample) -> None:
        """
        Adds an example value that will be used when learning a program to split the column.

        .. note::

            If an identical example is already present, this will do nothing.
            If a conflicting example is given (identical source but different results), an exception will be raised.

        :param example: Tuple of source value and list of intended splits. Source value could be provided as a string
            or a key value pair with source column as a key.
        """
        source = example[0]
        # handle string source value
        if isinstance(source, str):
            source = {self._source_column: source}

        # verify that source_data has all the required keys
        if self._source_column not in source:
            raise ValueError('Missing required source value for column ' + self._source_column)

        # check if example has the same number of splits
        if len(self._examples) > 0 and len(example[1]) != len(self._examples[0][1]):
            raise ValueError('Mismatched number of splits provided.')
        # check for duplicate examples
        for example_tuple in self._examples:
            source_duplicate = example_tuple[0] == source[self._source_column]
            if source_duplicate:
                if example_tuple[1] == example[1]:
                    # exactly same example found, do nothing
                    return
                else:
                    raise ValueError('Detected conflicting example. Another example with the same source but'
                                     ' different splits already exists.')

        self._dirty = True
        self._arguments['delimiters'] = []
        self._examples.append((source[self._source_column], example[1]))

    # noinspection PyUnresolvedReferences
    def list_examples(self) -> 'pandas.DataFrame':
        """
        Gets examples that are currently used to generate a program to split a column.

        :return: pandas.DataFrame with examples.
        :rtype: pandas.DataFrame
        """
        list_of_examples = [{'source': example_tuple[0],
                             **{'split_' + str(index): split for index, split in enumerate(example_tuple[1])}}
                            for example_tuple in self._examples]
        return _to_pandas_dataframe(list_of_examples)

    def delete_example(self, example_index: int):
        """
        Deletes example, so it's no longer considered in program generation.

        :param example_index: index of example to delete.
        """

        self._examples = self._examples[:example_index] + self._examples[example_index + 1:]
        self._dirty = True

    # noinspection PyUnresolvedReferences
    def generate_suggested_examples(self) -> 'pandas.DataFrame':
        """
        List examples that, if provided, would improve confidence in the generated program.

        .. note::

            This operation will internally make a pull on the data in order to generate suggestions.

        :return: pandas.DataFrame of suggested examples.
        :rtype: pandas.DataFrame
        """
        self._ensure_learn()
        blocks = steps_to_block_datas(self._dataflow._get_steps())
        blocks.append(self._split_column_step)
        response = self._engine_api.anonymous_send_message_to_block(
            AnonymousSendMessageToBlockMessageArguments(blocks=blocks,
                                                        message='getSuggestedInputs',
                                                        message_arguments=None)).to_pod()
        list_of_suggestions = [si['input'] for si in response['data']['significantInputs']] \
            if response['data']['significantInputs'] is not None else []
        return _to_pandas_dataframe({self._source_column: list_of_suggestions})

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Uses the program learned based on the provided examples to derive a new column and create a new dataflow.

        :return: A new Dataflow with a derived column.
        """
        self._ensure_learn()
        args = self._split_column_step.arguments.to_pod()
        return self._dataflow.add_step('Microsoft.DPrep.SplitColumnByExampleBlock', args)

    def __repr__(self):
        return dedent("""\
                SplitColumnByExampleBuilder
                    source_column: {0!s}
                    keep_delimiters: {1!s}
                    delimiters: {2!s}
                    example_count: {3!s}
                    has_program: {4!s}
                """.format(self._source_column,
                           self._arguments['keepDelimiter'] if len(self._examples) == 0 else 'N/A',
                           self.delimiters if len(self._examples) == 0 else 'N/A',
                           len(self._examples) if len(self.delimiters) == 0 else 'N/A',
                           self._arguments['dsl'] is not None))


class ImputeColumnArguments:
    """
    Defines and stores the arguments which can affect learning on a 'ImputeMissingValuesBuilder'.

    :var column_id: Column to impute.
    :var impute_function: The function to calculate the value to impute missing.
    :var custom_impute_value: The custom value used to impute missing.
    :var string_missing_option: The option to specify string values to be considered as missing.
    """

    def __init__(self,
                 column_id: str,
                 impute_function: Optional[ReplaceValueFunction] = ReplaceValueFunction.CUSTOM,
                 custom_impute_value: Optional[Any] = None,
                 string_missing_option: StringMissingReplacementOption = StringMissingReplacementOption.NULLSANDEMPTY):

        if custom_impute_value is not None and impute_function != ReplaceValueFunction.CUSTOM:
            raise ValueError("impute_function must be CUSTOM when custom_impute_value is specified.")
        if impute_function == ReplaceValueFunction.CUSTOM and custom_impute_value is None:
            raise ValueError("custom_impute_value must be specified when impute_function is CUSTOM.")
        self.column_id = column_id
        self.impute_function = impute_function
        self.custom_impute_value = custom_impute_value
        self.string_missing_option = string_missing_option


class ImputeMissingValuesBuilder:
    """
    Interactive object that can be used to learn a fixed program that imputes missing values in specified columns.
    """

    def __init__(self,
                 dataflow: 'dataprep.Dataflow',
                 engine_api: EngineAPI,
                 impute_columns: List[ImputeColumnArguments] = None,
                 group_by_columns: Optional[List[str]] = None):
        self._dataflow = dataflow
        self._engine_api = engine_api
        self._impute_missing_values_step = None
        self.impute_columns = impute_columns
        self.group_by_columns = group_by_columns

    def learn(self) -> None:
        """
        Learn a fixed program that imputes missing values in specified columns.
        """
        preceding_blocks = steps_to_block_datas(self._dataflow._get_steps())
        block_args = BlockArguments(
            block_type='Microsoft.DPrep.ReplaceMissingValuesBlock',
            arguments=PropertyValues.from_pod({
                'replaceColumns': [self._to_replace_column_args(args) for args in self.impute_columns],
                'groupByColumns': self.group_by_columns or []
            }))
        self._impute_missing_values_step = self._engine_api.add_block_to_list(
            AddBlockToListMessageArguments(new_block_arguments=block_args,
                                           blocks=preceding_blocks))

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Uses the learned program to impute missing values in specified columns and create a new dataflow.

        :return: A new Dataflow with missing value imputed.
        """
        self._ensure_learn()
        args = self._impute_missing_values_step.arguments.to_pod()
        return self._dataflow.add_step('Microsoft.DPrep.ReplaceMissingValuesBlock', args)

    def _ensure_learn(self):
        if self._impute_missing_values_step is None:
            self.learn()

    @staticmethod
    def _to_replace_column_args(impute_column_args: ImputeColumnArguments) -> Dict[str, Any]:
        args = {
            'columnId': impute_column_args.column_id,
            'replaceFunction': impute_column_args.impute_function,
            'stringReplacementOption': impute_column_args.string_missing_option
        }
        value = impute_column_args.custom_impute_value
        if isinstance(value, str):
            args['type'] = FieldType.STRING
            args['stringValue'] = value
        elif isinstance(value, int) or isinstance(value, float):
            args['type'] = FieldType.DECIMAL
            args['doubleValue'] = value
        elif isinstance(value, bool):
            args['type'] = FieldType.BOOLEAN
            args['booleanValue'] = value
        elif isinstance(value, datetime.datetime):
            args['type'] = FieldType.DATE
            args['datetimeValue'] = value
        return args


class JoinBuilder:
    """
    An interactive object that can be used to help join two Dataflows.

    .. note::

        This builder has the ability to detect and suggest potential join arguments. In some cases, the builder can derive the join key in one of the Dataflows and use the derived key column to perform a join.
    """
    def __init__(self,
                 engine_api: EngineAPI,
                 left_dataflow: 'dataprep.DataflowReference',
                 right_dataflow: 'dataprep.DataflowReference',
                 join_key_pairs: List[Tuple[str, str]] = None,
                 join_type: JoinType = JoinType.MATCH,
                 left_column_prefix: str = 'l_',
                 right_column_prefix: str = 'r_'):
        self._engine_api = engine_api
        self._left_dataflow = left_dataflow
        self._arguments = {
            'leftActivityReference': make_activity_reference(left_dataflow),
            'rightActivityReference': make_activity_reference(right_dataflow),
            'joinType': join_type,
            'leftNonPrefixedColumns': [],
            'rightNonPrefixedColumns': []
        }

        self._generated_column_name = None
        self._suggestions = None
        self._suggestion_applied = None

        # call property setters to perform additional validation
        self.left_column_prefix = left_column_prefix
        self.right_column_prefix = right_column_prefix
        self.join_key_pairs = join_key_pairs

    @property
    def join_type(self) -> JoinType:
        """Type of join to perform."""
        return self._arguments['joinType']

    @join_type.setter
    def join_type(self, value: JoinType):
        self._arguments['joinType'] = value

    @property
    def join_key_pairs(self) -> List[Tuple[str, str]]:
        """
        List of join key pairs represented as a list of tuples where the first value is a column name from left Dataflow
            and second value is a column name from right Dataflow.
        """
        pairs = self._arguments['joinKeyPairs']
        return None if pairs is None else [(pair['leftKeyColumn'], pair['rightKeyColumn']) for pair in pairs]

    @join_key_pairs.setter
    def join_key_pairs(self, value: List[Tuple[str, str]]):
        self._arguments['joinKeyPairs'] = None if value is None else [{'leftKeyColumn': pair[0], 'rightKeyColumn': pair[1]} for pair in value]

    @property
    def left_column_prefix(self) -> str:
        """
        Prefix to use on all columns from left dataflow.
        """
        return self._arguments['leftColumnPrefix']

    @left_column_prefix.setter
    def left_column_prefix(self, value: str):
        if value is None or not isinstance(value, str) or value == '':
            raise ValueError('Column prefix must be a non-empty string.')
        self._arguments['leftColumnPrefix'] = value

    @property
    def right_column_prefix(self) -> str:
        """
        Prefix to use on all columns from right dataflow.
        """
        return self._arguments['rightColumnPrefix']

    @right_column_prefix.setter
    def right_column_prefix(self, value: str):
        if value is None or not isinstance(value, str) or value == '':
            raise ValueError('Column prefix must be a non-empty string.')
        self._arguments['rightColumnPrefix'] = value

    def list_join_suggestions(self) -> str:
        """
        Suggested join variants.
        """
        if self._suggestions is None:
            self.generate_suggested_join()
        return repr([{i: self._pprint_suggestion(s)} for i, s in enumerate(self._suggestions)])

    @staticmethod
    def _pprint_suggestion(s: JoinSuggestionResult) -> str:
        return dedent("""
            Suggestion:
                Left:
                    Needs transform: {0!s}
                    % of matched rows: {1!s}
                Right:
                    Needs transform: {2!s}
                    % of matched rows: {3!s}
                Join keys: {4!r}

            """.format(
            s.left_suggestion.needs_transform,
            s.left_suggestion.joined_rows_percentage,
            s.right_suggestion.needs_transform,
            s.right_suggestion.joined_rows_percentage,
            [(s.join_keys['leftKeyColumn'], s.join_keys['rightKeyColumn'])]))

    def detect_column_info(self) -> None:
        """
        This performs a pull on provided Dataflows to automatically set left and right column prefixes and non-prefixed columns.
        """
        join_block = step_to_block_data(Step(step_type='TwoWayJoin', arguments=self._arguments))
        column_info_response = self._engine_api.anonymous_send_message_to_block(
            AnonymousSendMessageToBlockMessageArguments(blocks=[join_block],
                                                        message='getColumnInformationForJoin',
                                                        message_arguments={
                                                            'leftPrefixBase': self._arguments['leftColumnPrefix'],
                                                            'rightPrefixBase': self._arguments['rightColumnPrefix']
                                                        }).to_pod())
        info = column_info_response.data
        self._arguments['leftColumnPrefix'] = info['leftColumnPrefix']
        self._arguments['rightColumnPrefix'] = info['rightColumnPrefix']
        self._arguments['leftNonPrefixedColumns'] = info['leftNonPrefixedColumns']
        self._arguments['rightNonPrefixedColumns'] = info['rightNonPrefixedColumns']
        self._generated_column_name = info['generatedKeyColumnName']

    def generate_suggested_join(self) -> None:
        """
        This pulls the data from both left and right Dataflows to analyze it and try to come up with potential join
            arguments based on it.

        .. remarks::

            The resulting join suggestion could either use existing columns in the provided
                Dataflows or could generate a key column derived from an existing column in one of the Dataflows.
                For instance, if one Dataflow has a column 'Full name' with values like 'Smith, John' and the other Dataflow has
                columns 'First Name' and 'Last Name' with values like 'John', 'Smith' the join suggestion might be to derive a
                new column in the second Dataflow (called KEY_GENERATED{_n}) by concatenating 'Last Name' and 'First Name' with
                a comma in between and then use the derived column in the right Dataflow and 'Full Name' column in the left
                Dataflow to perform a join.
        """
        self._ensure_column_info()
        join_block = step_to_block_data(Step(step_type='TwoWayJoin', arguments=self._arguments))
        join_suggestions_response = self._engine_api.anonymous_send_message_to_block(
            AnonymousSendMessageToBlockMessageArguments(blocks=[join_block],
                                                        message='generateJoinSuggestions',
                                                        message_arguments={'generatedKeyColumnName': self._generated_column_name}).to_pod())

        suggestions_data = join_suggestions_response.data['joinSuggestions']
        self._suggestions = [] if suggestions_data is None or len(suggestions_data) == 0 else [JoinSuggestionResult.from_pod(s)
            for s in suggestions_data]

    def apply_suggestion(self, suggestion_index: int) -> None:
        """
        Applies the join suggestion's parameters to builder's arguments.

        :param suggestion_index: Index of join suggestion to apply.
        """
        suggestion = self._suggestions[suggestion_index]
        if suggestion is None:
            raise ValueError('Invalid suggestion index')

        self._arguments['joinKeyPairs'] = [
            {
                'leftKeyColumn': suggestion.join_keys['leftKeyColumn'],
                'rightKeyColumn': suggestion.join_keys['rightKeyColumn']
            }
        ]
        if suggestion.left_suggestion.needs_transform:
            self._arguments['leftActivityReference'] = suggestion.left_suggestion.activity_reference_to_use
        if suggestion.right_suggestion.needs_transform:
            self._arguments['rightActivityReference'] = suggestion.right_suggestion.activity_reference_to_use

        self._suggestion_applied = suggestion

    def preview(self, skip: int = 0, count: int = 10) -> 'pandas.DataFrame':
        """
        Preview of the join result.

        :param skip: Number of rows to skip. Allows you to move preview window forward. Default is 0.
        :param count: Number of rows to preview. Default is 10.
        :param count: Number of rows to preview. Default is 10.
        :return: pandas.DataFrame with preview data.
        :rtype: pandas.DataFrame
        """
        return self.to_dataflow() \
            .skip(skip) \
            .head(count)

    def to_dataflow(self):
        """
        Uses current state of the builder to create a new Dataflow by joining two provided Dataflows.

        :return: New Dataflow.
        """
        if self._arguments['joinKeyPairs'] is None:
            raise ValueError("Join keys are required.")
        from .dataflow import Dataflow
        return Dataflow.join(self._arguments['leftActivityReference'],
                             self._arguments['rightActivityReference'],
                             [(pair['leftKeyColumn'], pair['rightKeyColumn']) for pair in self._arguments['joinKeyPairs']],
                             self._arguments['joinType'],
                             self._arguments['leftColumnPrefix'],
                             self._arguments['rightColumnPrefix'],
                             self._arguments['leftNonPrefixedColumns'],
                             self._arguments['rightNonPrefixedColumns'])

    def _ensure_column_info(self) -> None:
        if self._generated_column_name is None:
            self.detect_column_info()

    def __repr__(self):
        return dedent("""\
                    JoinBuilder:
                        join_key_pairs: {0!r}
                        left_column_prefix: {1!s}
                        right_column_prefix: {2!s}
                        left_non_prefixed_columns: {3!r}
                        right_non_prefixed_columns: {4!r}
                        is_join_suggestion_applied: {5!s}
                        is_suggested_join_key_generated: {6:s}
                    """.format(
            [(pair['leftKeyColumn'], pair['rightKeyColumn']) for pair in self._arguments['joinKeyPairs']]
            if self._arguments['joinKeyPairs'] is not None else None,
            self._arguments['leftColumnPrefix'],
            self._arguments['rightColumnPrefix'],
            self._arguments['leftNonPrefixedColumns'],
            self._arguments['rightNonPrefixedColumns'],
            'False' if self._suggestion_applied is None else 'True',
            self._is_join_key_generated()))

    def _is_join_key_generated(self) -> str:
        if self._suggestion_applied is None:
            return 'N/A'

        if self._suggestion_applied['leftSuggestion']['needsTransform']:
            return 'True'
        if self._suggestion_applied['rightSuggestion']['needsTransform']:
            return 'True'

        return 'False'


class QuantileTransformBuilder:
    """
    Interactive object that can be used for quantile transformation.

    .. remarks::

        This builder allows you to modify the number of quantiles and output distribution, and is able to learn and show
            the learnt quantile boundaries and corresponding quantiles.
    """

    def __init__(self, src_column: str, new_column: str, quantiles_count: int,
                 output_distribution: str, dataflow: 'dataprep.Dataflow', engine_api: EngineAPI):
        self._engine_api = engine_api
        self._dataflow = dataflow
        self._src_column = src_column
        self._new_column = new_column
        self._arguments = {
            'column': ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN,
                                      details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(src_column))),
            'newColumnName': new_column,
            'quantilesCount': quantiles_count,
            'outputDistribution': output_distribution
        }
        self._local_data = {}

    @property
    def quantiles_count(self) -> int:
        """
        The number of quantiles used. This will be used to discretize the cdf.
        """
        return self._arguments['quantilesCount']

    @quantiles_count.setter
    def quantiles_count(self, value):
        self._arguments['quantilesCount'] = value

    @property
    def output_distribution(self) -> str:
        """
        The distribution of the transformed data.
        """
        return self._arguments['outputDistribution']

    @output_distribution.setter
    def output_distribution(self, value):
        self._arguments['outputDistribution'] = value

    @property
    def quantiles(self):
        """
        The learnt quantile boundaries.
        """
        return self._local_data.get('quantiles')

    @property
    def quantiles_values(self):
        """
        The learnt quantiles.
        """
        return self._local_data.get('quantilesValues')

    def learn(self) -> None:
        """
        Learn the quantile boundaries and quantiles which will be used to quantile transform the source column.
        """
        blocks = steps_to_block_datas(self._dataflow._get_steps())
        new_block = self._engine_api.add_block_to_list(AddBlockToListMessageArguments(
            blocks=blocks,
            new_block_arguments=BlockArguments(PropertyValues.from_pod(self._arguments),
                                               'Microsoft.DPrep.QuantileTransformBlock',
                                               PropertyValues.from_pod(self._local_data)),
        ))
        self._local_data = new_block.local_data.to_pod()
        if self._need_learning():
            raise ValueError('Failed to learn quantiles or quantiles value.')

    def to_dataflow(self) -> 'dataprep.Dataflow':
        """
        Returns a new Dataflow with the quantile transformation step added to the end of the current Dataflow and with
        all the parameters learnt.
        """

        self._ensure_learnt()
        return self._dataflow.add_step('Microsoft.DPrep.QuantileTransformBlock', self._arguments)

    def _ensure_learnt(self) -> None:
        if self._need_learning():
            self.learn()

    def _need_learning(self) -> bool:
        return QuantileTransformBuilder._none_or_empty(self._local_data.get('quantiles')) \
            or QuantileTransformBuilder._none_or_empty(self._local_data.get('quantilesValues'))

    @staticmethod
    def _none_or_empty(collection):
        return collection is None or len(collection) == 0

    def __repr__(self):
        return dedent("""\
            QuantileTransformBuilder
                src_column: '{0!s}'
                new_column: '{1!s}'
                quantiles_count: {2!s}
                output_distribution: {3!s}
            """.format(self._src_column, self._new_column, self.quantiles_count, self.output_distribution))


class Builders:
    """
    Exposes all available builders for a given Dataflow.
    """
    def __init__(self, dataflow: 'dataprep.Dataflow', engine_api: EngineAPI):
        self._dataflow = dataflow
        self._engine_api = engine_api

    def detect_file_format(self) -> FileFormatBuilder:
        """
        Constructs an instance of :class:`FileFormatBuilder`.
        """
        return FileFormatBuilder(self._dataflow, self._engine_api)

    def set_column_types(self) -> ColumnTypesBuilder:
        """
        Constructs an instance of :class:`ColumnTypesBuilder`.
        """
        return ColumnTypesBuilder(self._dataflow, self._engine_api)

    def extract_table_from_json(self, encoding: FileEncoding = FileEncoding.UTF8) -> JsonTableBuilder:
        """
        Constructs an instance of :class:`JsonTableBuilder`.
        """
        return JsonTableBuilder(self._dataflow, self._engine_api, encoding=encoding)

    def derive_column_by_example(self, source_columns: List[str], new_column_name: str) -> DeriveColumnByExampleBuilder:
        """
        Constructs an instance of :class:`DeriveColumnByExampleBuilder`.
        """
        return DeriveColumnByExampleBuilder(self._dataflow, self._engine_api, source_columns, new_column_name)

    def one_hot_encode(self, source_column: str, prefix: str) -> OneHotEncodingBuilder:
        """
        Constructs an instance of :class:`OneHotEncodingBuilder`.
        """
        return OneHotEncodingBuilder(self._dataflow,
                                     self._engine_api,
                                     source_column,
                                     prefix)

    def label_encode(self,
                     source_column: str,
                     new_column_name: str) -> LabelEncoderBuilder:
        """
        Constructs an instance of :class:`LabelEncoderBuilder`.
        """
        return LabelEncoderBuilder(self._dataflow,
                                   self._engine_api,
                                   source_column,
                                   new_column_name)

    def pivot(self,
              columns_to_pivot: List[str],
              value_column: str,
              summary_function: SummaryFunction = None,
              group_by_columns: List[str] = None,
              null_value_replacement: str = None,
              error_value_replacement: str = None) -> PivotBuilder:
        """
        Constructs an instance of :class:`PivotBuilder`.
        """
        return PivotBuilder(self._dataflow,
                            self._engine_api,
                            columns_to_pivot,
                            value_column,
                            summary_function,
                            group_by_columns,
                            null_value_replacement,
                            error_value_replacement)

    def min_max_scale(self,
                      column: str,
                      range_min: float = 0,
                      range_max: float = 1,
                      data_min: float = None,
                      data_max: float = None) -> MinMaxScalerBuilder:
        """
        Constructs an instance of :class:`MinMaxScalerBuilder`.
        """
        return MinMaxScalerBuilder(self._dataflow, self._engine_api, column, range_min, range_max, data_min, data_max)

    def fuzzy_group_column(self,
                           source_column: str,
                           new_column_name: str,
                           similarity_threshold: float = 0.8,
                           similarity_score_column_name: str = None) -> FuzzyGroupBuilder:
        """
        Constructs an instance of :class:`FuzzyGroupBuilder`.
        """
        return FuzzyGroupBuilder(self._dataflow,
                                 self._engine_api,
                                 source_column,
                                 new_column_name,
                                 similarity_threshold,
                                 similarity_score_column_name)

    def split_column_by_example(self,
                                source_column: str,
                                keep_delimiters: bool = False,
                                delimiters: List[str] = None) -> SplitColumnByExampleBuilder:
        """
        Constructs an instance of :class:`SplitColumnByExampleBuilder`.
        """
        return SplitColumnByExampleBuilder(self._dataflow,
                                           self._engine_api,
                                           source_column,
                                           keep_delimiters,
                                           delimiters)

    def impute_missing_values(self,
                              impute_columns: List[ImputeColumnArguments] = None,
                              group_by_columns: Optional[List[str]] = None) -> ImputeMissingValuesBuilder:
        """
        Constructs an instance of :class:`ImputeMissingValuesBuilder`.
        """
        return ImputeMissingValuesBuilder(self._dataflow,
                                          self._engine_api,
                                          impute_columns,
                                          group_by_columns)

    def join(self,
             right_dataflow: 'dataprep.DataflowReference',
             join_key_pairs: List[Tuple[str, str]] = None,
             join_type: JoinType = JoinType.MATCH,
             left_column_prefix: str = 'l_',
             right_column_prefix: str = 'r_') -> JoinBuilder:
        """
        Constructs an instance of :class:`JoinBuilder`.
        """
        return JoinBuilder(self._engine_api,
                           self._dataflow,
                           right_dataflow,
                           join_key_pairs,
                           join_type,
                           left_column_prefix,
                           right_column_prefix)

    def quantile_transform(self, source_column: str, new_column: str,
                           quantiles_count: int = 1000, output_distribution: str = "Uniform"):
        """
        Constructs an instance of :class:`QuantileTransformBuilder`.
        """
        return QuantileTransformBuilder(
            src_column=source_column, new_column=new_column, quantiles_count=quantiles_count,
            output_distribution=output_distribution, dataflow=self._dataflow, engine_api=self._engine_api)
