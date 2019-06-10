# Copyright (c) Microsoft Corporation. All rights reserved.
from .engineapi.api import EngineAPI, get_engine_api
from .engineapi import typedefinitions
from .engineapi.typedefinitions import (SkipMode, PromoteHeadersMode, FileEncoding,
                                        ExecuteAnonymousBlocksMessageArguments,
                                        ColumnsSelectorDetails, ColumnsSelectorType, SingleColumnSelectorDetails,
                                        ColumnsSelector, CodeBlockType, FieldType,
                                        ActivityReference, GetSecretsMessageArguments, PropertyValues,
                                        AssertPolicy, AddBlockToListMessageArguments, BlockArguments, ValueKind,
                                        InspectorArguments, ExecuteInspectorCommonResponse, AnonymousActivityData,
                                        AnonymousBlockData, SaveActivityFromDataMessageArguments,
                                        GetSourceDataHashMessageArguments)
from .errorhandlers import EmptyStepsError, PandasImportError
from ._pandas_helper import have_pandas
from .dataprofile import DataProfile, _Inspector
from .datasources import MSSQLDataSource, PostgreSQLDataSource, LocalDataSource, DataSource, FileOutput, DataDestination, FileDataSource
from .references import make_activity_reference, ExternalReference, _to_anonymous_reference
from .step import (Step, steps_to_block_datas, single_column_to_selector_value, MultiColumnSelection,
                   column_selection_to_selector_value)
from .builders import Builders
from .typeconversions import (TypeConverter, DateTimeConverter)
from .types import SplitExample, Delimiters
from .expressions import Expression, col
from ._archiveoption import ArchiveOptions
from ._datastore_helper import (datastore_to_dataflow, get_datastore_value, _is_datapath, _is_datapaths, Datastore,
                                Datastores)
from ._loggerfactory import _LoggerFactory, track
from .sparkexecution import SparkExecutor
from typing import List, Dict, cast, Tuple, TypeVar, Optional, Any, Union
from pathlib import Path
from textwrap import dedent, indent
from copy import copy
from collections import Iterable
import random
import tempfile
import datetime
from uuid import uuid4
from shutil import rmtree
import os
from enum import Enum

FilePath = TypeVar('FilePath', FileDataSource, str, Datastores)
DatabaseSource = TypeVar('DatabaseSource', MSSQLDataSource, PostgreSQLDataSource, Datastore)
DataflowReference = TypeVar('DataflowReference', 'Dataflow', ExternalReference, 'Dataset', 'DatasetDefinition')

logger = None


def get_logger():
    global logger
    if logger is not None:
        return logger

    logger = _LoggerFactory.get_logger("Dataflow")
    return logger

class DataflowValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


# >>> BEGIN GENERATED CLASSES
class SummaryFunction(Enum):
    """
    Enum SummaryFunction.

    .. remarks::

        Possible enum values are:
        - MIN: Minimum value.
        - MAX: Maximum value.
        - MEAN: Mean value.
        - MEDIAN: Median value.
        - VAR: Variance value.
        - SD: Standard deviance value.
        - COUNT: Total count.
        - SUM: Sum of all value.
        - SKEWNESS: Skewness value.
        - KURTOSIS: Kurtosis value.
    """
    MIN = 0
    MAX = 1
    MEAN = 2
    MEDIAN = 3
    VAR = 4
    SD = 5
    COUNT = 8
    SUM = 11
    SKEWNESS = 18
    KURTOSIS = 19


class MismatchAsOption(Enum):
    """
    Enum MismatchAsOption.

    .. remarks::

        Possible enum values are:
        - ASTRUE: Mismatch value as true.
        - ASFALSE: Mismatch value as false.
        - ASERROR: Mismatch value as error.
    """
    ASTRUE = 0
    ASFALSE = 1
    ASERROR = 2


class TrimType(Enum):
    """
    Enum TrimType.

    .. remarks::

        Possible enum values are:
        - WHITESPACE: Trim white space.
        - CUSTOM: Trim custom characters.
    """
    WHITESPACE = 0
    CUSTOM = 1


class DecimalMark(Enum):
    """
    Enum DecimalMark.

    .. remarks::

        Possible enum values are:
        - DOT: Using dot as decimal mark.
        - COMMA: Using comma as decimal mark.
    """
    DOT = 0
    COMMA = 1


class JoinType(Enum):
    """
    Describes different possible types of join.

    .. remarks::

        Possible enum values are:
        - MATCH: Only records with matching join keys will be returned.
        - INNER: Only records with matching join keys will be returned.
        - UNMATCHLEFT: Records from left data set that did not match with anything.
        - LEFTANTI: Records from left data set that did not match with anything.
        - LEFTOUTER: All records from left data set and only matching records from the right data set.
        - UNMATCHRIGHT: Records from right data set that did not match with anything.
        - RIGHTANTI: Records from right data set that did not match with anything.
        - RIGHTOUTER: All records from right data set and only matching records from the right data set.
        - FULLANTI: Only unmatched records from left and right data sets.
        - FULL: All records from both left and right data sets.
    """
    NONE = 0
    MATCH = 2
    INNER = 2
    UNMATCHLEFT = 4
    LEFTANTI = 4
    LEFTOUTER = 6
    UNMATCHRIGHT = 8
    RIGHTANTI = 8
    RIGHTOUTER = 10
    FULLANTI = 12
    FULL = 14


class SkipMode(Enum):
    """
    Defines a strategy to skip rows when reading files

    .. remarks::

        Possible enum values are:
        - NONE: Don't skip any rows.
        - UNGROUPED: Skip rows from the first file only.
        - FIRSTFILE: Skip rows from the first file only.
        - GROUPED: Skip rows from every file.
        - ALLFILES: Skip rows from every file.
    """
    NONE = 0
    UNGROUPED = 1
    FIRSTFILE = 1
    GROUPED = 2
    ALLFILES = 2


class PromoteHeadersMode(Enum):
    """
    Defines strategy to promote headers when reading files

    .. remarks::

        Possible enum values are:
        - NONE: Do not promote headers. Use when file(s) has no headers.
        - UNGROUPED: Promote headers from the first file. All subsequent files are considered to be just data.
        - FIRSTFILE: Promote headers from the first file. All subsequent files are considered to be just data.
        - GROUPED: Promote headers from every file. Allows to read files with inconsistent schema.
        - ALLFILES: Promote headers from every file. Allows to read files with inconsistent schema.
        - CONSTANTGROUPED: Optimized option for the case when all the files have exactly same headers. In effect this will promote headers from the first file and skip a row for every other file.
        - SAMEALLFILES: Optimized option for the case when all the files have exactly same headers. In effect this will promote headers from the first file and skip a row for every other file.
    """
    NONE = 0
    UNGROUPED = 1
    FIRSTFILE = 1
    GROUPED = 2
    ALLFILES = 2
    CONSTANTGROUPED = 3
    SAMEALLFILES = 3


class SType(Enum):
    """
    Defines suported semantic types

    .. remarks::

        Possible enum values are:
        - EMAILADDRESS: Email address.
        - GEOGRAPHICCOORDINATE: Common representations of geographic coordinates.
        - IPV4ADDRESS: IPv4 address.
        - IPV6ADDRESS: IPv6 address.
        - USPHONENUMBER: Common formats of US phone numbers.
        - ZIPCODE: Common formats of US ZIP code.
    """
    EMAILADDRESS = 0
    GEOGRAPHICCOORDINATE = 1
    IPV4ADDRESS = 2
    IPV6ADDRESS = 3
    USPHONENUMBER = 4
    ZIPCODE = 5


class DatastoreValue:
    """
    Properties uniquely identifying a datastore.

    :param subscription: The subscription the workspace belongs to.
    :param resource_group: The resource group the workspace belongs to.
    :param workspace_name: The workspace the datastore belongs to.
    :param datastore_name: The datastore to read the data from.
    :param path: The path on the datastore.
    """
    def __init__(self,
                 subscription: str,
                 resource_group: str,
                 workspace_name: str,
                 datastore_name: str,
                 path: str = ''):
        self.subscription = subscription
        self.resource_group = resource_group
        self.workspace_name = workspace_name
        self.datastore_name = datastore_name
        self.path = path

    def _to_pod(self) -> Dict[str, Any]:
        return {
            'subscription': self.subscription,
            'resourceGroup': self.resource_group,
            'workspaceName': self.workspace_name,
            'datastoreName': self.datastore_name,
            'path': self.path,
        }


class ReplacementsValue:
    """
    The values to replace and their replacements.

    :param source_value: The value to replace.
    :param target_value: The replacement value.
    """
    def __init__(self,
                 source_value: str,
                 target_value: Optional[str] = None):
        self.source_value = source_value
        self.target_value = target_value

    def _to_pod(self) -> Dict[str, Any]:
        return {
            'sourceValue': self.source_value,
            'targetValue': self.target_value,
        }


class HistogramArgumentsValue:
    """
    Additional arguments required for Histogram summary function.

    :param histogram_bucket_count: Number of buckets to use.
    """
    def __init__(self,
                 histogram_bucket_count: int):
        self.histogram_bucket_count = histogram_bucket_count

    def _to_pod(self) -> Dict[str, Any]:
        return {
            'histogramBucketCount': self.histogram_bucket_count,
        }


class KernelDensityArgumentsValue:
    """
    Additional arguments required for KernelDensity summary function.

    :param kernel_density_point_count: Number of kernel density points to calculate.
    :param kernel_density_bandwidth: Kernel density bandwidth.
    """
    def __init__(self,
                 kernel_density_point_count: int,
                 kernel_density_bandwidth: float):
        self.kernel_density_point_count = kernel_density_point_count
        self.kernel_density_bandwidth = kernel_density_bandwidth

    def _to_pod(self) -> Dict[str, Any]:
        return {
            'kernelDensityPointCount': self.kernel_density_point_count,
            'kernelDensityBandwidth': self.kernel_density_bandwidth,
        }


class SummaryColumnsValue:
    """
    Column summarization definition.

    :param column_id: Column to summarize.
    :param summary_function: Aggregation function to use.
    :param summary_column_name: Name of the new column holding the aggregate values.
    :param histogram_arguments: Additional arguments required for Histogram summary function.
    :param kernel_density_arguments: Additional arguments required for KernelDensity summary function.
    :param quantiles: Quantile boundary values required for Quantiles summary function.
    """
    def __init__(self,
                 column_id: str,
                 summary_function: SummaryFunction,
                 summary_column_name: str,
                 histogram_arguments: Optional[HistogramArgumentsValue] = None,
                 kernel_density_arguments: Optional[KernelDensityArgumentsValue] = None,
                 quantiles: Optional[List[float]] = None):
        self.column_id = column_id
        self.summary_function = summary_function
        self.summary_column_name = summary_column_name
        self.histogram_arguments = histogram_arguments
        self.kernel_density_arguments = kernel_density_arguments
        self.quantiles = quantiles

    def _to_pod(self) -> Dict[str, Any]:
        return {
            'columnId': self.column_id,
            'summaryFunction': self.summary_function,
            'summaryColumnName': self.summary_column_name,
            'histogramArguments': self.histogram_arguments,
            'kernelDensityArguments': self.kernel_density_arguments,
            'quantiles': self.quantiles,
        }
# <<< END GENERATED CLASSES


class Dataflow:
    """
    A Dataflow represents a series of lazily-evaluated, immutable operations on data.
        It is only an execution plan. No data is loaded from the source until you get data from the Dataflow using one of `head`, `to_pandas_dataframe`, `get_profile` or the write methods.

    .. remarks::

        Dataflows are usually created by supplying a data source. Once the data source has been provided, operations
            can be added by invoking the different transformation methods available on this class. The result of adding
            an operation to a Dataflow is always a new Dataflow.

        The actual loading of the data and execution of the transformations is delayed as much as possible and will not
            occur until a 'pull' takes place. A pull is the action of reading data from a Dataflow, whether by asking to
            look at the first N records in it or by transferring the data in the Dataflow to another storage mechanism
            (a Pandas Dataframe, a CSV file, or a Spark Dataframe).

        The operations available on the Dataflow are runtime-agnostic. This allows the transformation pipelines
            contained in them to be portable between a regular Python environment and Spark.
    """

    def __init__(self, engine_api: EngineAPI, steps: List[Step] = None):
        self._engine_api = engine_api
        self._steps = steps if steps is not None else []

        self.builders = Builders(self, engine_api)
        self._spark_executor = SparkExecutor(engine_api)

    def add_step(self,
                 step_type: str,
                 arguments: Dict[str, Any],
                 local_data: Dict[str, Any] = None) -> 'Dataflow':
        new_step = Step(step_type, arguments, local_data)
        return Dataflow(self._engine_api, self._steps + [new_step])

    @staticmethod
    def _get_property_value(property, property_name: str):
        return property[property_name] if isinstance(property, dict) else property.to_pod()[property_name]

    def _get_steps(self) -> List[Step]:
        return [s for s in self._steps]

    def _execute_inspector(self, inspector: Union[str, InspectorArguments]) -> ExecuteInspectorCommonResponse:
        self._raise_if_missing_secrets()
        return _Inspector._from_execution(
            self._engine_api,
            make_activity_reference(self),
            inspector)

    # noinspection PyUnresolvedReferences
    @track(get_logger)
    def get_profile(self, include_stype_counts: bool = False, number_of_histogram_bins: int = 10) -> DataProfile:
        """
        Requests the data profile which collects summary statistics on the full data produced by the Dataflow.
            A data profile can be very useful to understand the input data, identify anomalies and missing values,
            and verify that data preparation operations produced the desired result.

        :param include_stype_counts: Whether to include checking if values look like some well known semantic types of
            information. For Example, "email address". Turning this on will impact performance.
        :paramtype boolean
        :param number_of_histogram_bins: Number of bins in a histogram. If not specified will be set to 10.
        :paramtype int
        :return: DataProfile object
        :rtype: DataProfile
        """
        return self._get_profile(include_stype_counts, number_of_histogram_bins)

    def _get_profile(self,
                     include_stype_counts: bool = False,
                     number_of_histogram_bins: int = 10,
                     include_average_spaces_count: bool = False,
                     include_string_lengths: bool = False) -> DataProfile:
        """
        Actual get_profile implementation
        """
        self._raise_if_missing_secrets()
        activity_ref = _to_anonymous_reference(self)
        return DataProfile._from_execution(self._engine_api,
                                           activity_ref,
                                           include_stype_counts,
                                           number_of_histogram_bins,
                                           include_average_spaces_count,
                                           include_string_lengths)

    @property
    def dtypes(self) -> Dict[str, FieldType]:
        """
        Gets column data types for the current dataset by calling :meth:`get_profile` and extracting just dtypes from
            the resulting DataProfile.

        .. note:

            This will trigger a data profile calculation.
            To avoid calculating profile multiple times, get the profile first by calling \
            `get_profile()` and then inspect it.

        :return: A dictionary, where key is the column name and value is :class:`azureml.dataprep.FieldType`.
        """
        profile = self._get_profile()
        return profile.dtypes

    @property
    def row_count(self) -> int:
        """
        Count of rows in this Dataflow.

        .. note::

            This will trigger a data profile calculation. To avoid calculating profile multiple times, get the profile first by calling \
            `get_profile()` and then inspect it.

        .. note::

            If current Dataflow contains `take_sample` step or 'take' step, this will return number of rows in the \
            subset defined by those steps.

        :return: Count of rows.
        :rtype: int
        """
        profile = self._get_profile()
        return profile.row_count

    @property
    def shape(self) -> Tuple[int,int]:
        """
        Shape of the data produced by the Dataflow.

        .. note::

            This will trigger a data profile calculation. To avoid calculating profile multiple times, get the profile first by calling \
            `get_profile()` and then inspect it.

        .. note::

            If current Dataflow contains `take_sample` step or 'take' step, this will return number of rows in the \
            subset defined by those steps.

        :return: Tuple of row count and column count.
        """
        profile = self._get_profile()
        return profile.shape

    def head(self, count: int = 10) -> 'pandas.DataFrame':
        """
        Pulls the number of records specified from the top of this Dataflow and returns them as a `Link pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.

        :param count: The number of records to pull. 10 is default.
        :return: A Pandas `Link pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.
        """
        return self.take(count).to_pandas_dataframe(extended_types=True)

    @track(get_logger)
    def run_local(self) -> None:
        """
        Runs the current Dataflow using the local execution runtime.
        """
        self._raise_if_missing_secrets()
        self._engine_api.execute_anonymous_blocks(ExecuteAnonymousBlocksMessageArguments(
            blocks=steps_to_block_datas(self._steps)
        ))

    def run_spark(self) -> None:
        """
        Runs the current Dataflow using the Spark runtime.
        """
        self._raise_if_missing_secrets()
        return self._spark_executor.execute(steps_to_block_datas(self._steps), use_sampling=False)

    # noinspection PyUnresolvedReferences
    @track(get_logger)
    def to_pandas_dataframe(self, extended_types: bool = False, nulls_as_nan: bool = True) -> 'pandas.DataFrame':
        """
        Pulls all of the data and returns it as a Pandas `Link pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.

        .. remarks::

            This method will load all the data returned by this Dataflow into memory.

            Since Dataflows do not require a fixed, tabular schema but Pandas DataFrames do, an implicit tabularization
                step will be executed as part of this action. The resulting schema will be the union of the schemas of all
                records produced by this Dataflow.

        :param extended_types: Whether to keep extended DataPrep types such as DataPrepError in the DataFrame. If False,
            these values will be replaced with None.
        :param nulls_as_nan: Whether to interpret nulls (or missing values) in number typed columns as NaN. This is
            done by pandas for performance reasons; it can result in a loss of fidelity in the data.
        :return: A Pandas `Link pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.
        """
        if not have_pandas():
            raise PandasImportError()
        else:
            import pandas
        from azureml.dataprep.native import preppy_to_ndarrays
        from collections import OrderedDict

        random_id = uuid4()
        intermediate_path = Path(os.path.join(tempfile.gettempdir(), str(random_id)))
        try:
            dataflow_to_execute = self.add_step('Microsoft.DPrep.WriteDataSetBlock', {
                'outputPath': {
                    'target': 0,
                    'resourceDetails': [{'path': str(intermediate_path)}]
                },
                'profilingFields': ['Kinds', 'MissingAndEmpty']
            })

            self._raise_if_missing_secrets()
            self._engine_api.execute_anonymous_blocks(
                ExecuteAnonymousBlocksMessageArguments(blocks=steps_to_block_datas(dataflow_to_execute._steps)))

            intermediate_files = [str(p) for p in intermediate_path.glob('part-*')]
            intermediate_files.sort()
            dataset = preppy_to_ndarrays(intermediate_files, extended_types, nulls_as_nan)
            return pandas.DataFrame.from_dict(OrderedDict(dataset))
        finally:
            try:
                rmtree(intermediate_path)
            except:
                pass  # ignore exception

    # noinspection PyUnresolvedReferences
    @track(get_logger)
    def to_spark_dataframe(self) -> 'pyspark.sql.DataFrame':
        """
        Creates a Spark `Link pyspark.sql.DataFrame <https://spark.apache.org/docs/latest/api/python/pyspark.sql.html#pyspark.sql.DataFrame>`_ that can execute the transformation pipeline defined by this Dataflow.

        .. remarks::

            Since Dataflows do not require a fixed, tabular schema but Spark Dataframes do, an implicit tabularization
                step will be executed as part of this action. The resulting schema will be the union of the schemas of all
                records produced by this Dataflow. This tabularization step will result in a pull of the data.

            .. note::

                The Spark Dataframe returned is only an execution plan and doesn't actually contain any data, since Spark Dataframes are also lazily evaluated.

        :return: A Spark `Link pyspark.sql.DataFrame <https://spark.apache.org/docs/latest/api/python/pyspark.sql.html#pyspark.sql.DataFrame>`_.
        """
        self._raise_if_missing_secrets()
        return self._spark_executor.get_dataframe(steps_to_block_datas(self._steps), use_sampling=False)

    # noinspection PyUnresolvedReferences
    @track(get_logger)
    def verify_has_data(self):
        """
        Verifies that this Dataflow would produce records if executed. An exception will be thrown otherwise.
        """
        if len(self._steps) == 0:
            raise EmptyStepsError()

        profile = self.take(1)._get_profile()
        if profile.row_count == 0 or profile.row_count is None:
            raise DataflowValidationError("The Dataflow produced no records.")

    def parse_delimited(self,
                        separator: str,
                        headers_mode: PromoteHeadersMode,
                        encoding: FileEncoding,
                        quoting: bool,
                        skip_rows: int,
                        skip_mode: SkipMode,
                        comment: str) -> 'Dataflow':
        """
        Adds step to parse CSV data.

        :param separator: The separator to use to split columns.
        :param headers_mode: How to determine column headers.
        :param encoding: The encoding of the files being read.
        :param quoting: Whether to handle new line characters within quotes. This option will impact performance.
        :param skip_rows: How many rows to skip.
        :param skip_mode: The mode in which rows are skipped.
        :param comment: Character used to indicate a line is a comment instead of data in the files being read.
        :return: A new Dataflow with Parse Delimited Step added.
        """
        return self.add_step('Microsoft.DPrep.ParseDelimitedBlock', {
            'columnHeadersMode': headers_mode,
            'separator': separator,
            'commentLineCharacter': comment,
            'fileEncoding': encoding,
            'skipRowsMode': skip_mode,
            'skipRows': skip_rows,
            'handleQuotedLineBreaks': quoting
        })

    def parse_fwf(self,
                  offsets: List[int],
                  headers_mode: PromoteHeadersMode,
                  encoding: FileEncoding,
                  skip_rows: int,
                  skip_mode: SkipMode) -> 'Dataflow':
        """
        Adds step to parse fixed-width data.

        :param offsets: The offsets at which to split columns. The first column is always assumed to start at offset 0.
        :param headers_mode: How to determine column headers.
        :param encoding: The encoding of the files being read.
        :param skip_rows: How many rows to skip.
        :param skip_mode: The mode in which rows are skipped.
        :return: A new Dataflow with Parse FixedWidthFile Step added.
        """
        return self.add_step('Microsoft.DPrep.ParseFixedWidthColumns', {
            'columnHeadersMode': headers_mode,
            'columnOffsets': offsets,
            'fileEncoding': encoding,
            'skipRowsMode': skip_mode,
            'skipRows': skip_rows,
        })

    def parse_lines(self,
                    headers_mode: PromoteHeadersMode,
                    encoding: FileEncoding,
                    skip_rows: int,
                    skip_mode: SkipMode,
                    comment: str) -> 'Dataflow':
        """
        Adds step to parse text files and split them into lines.

        :param headers_mode: How to determine column headers.
        :param encoding: The encoding of the files being read.
        :param skip_rows: How many rows to skip.
        :param skip_mode: The mode in which rows are skipped.
        :param comment: Character used to indicate a line is a comment instead of data in the files being read.
        :return: A new Dataflow with Parse Lines Step added.
        """
        return self.add_step('Microsoft.DPrep.ParsePlainTextBlock', {
            'columnHeadersMode': headers_mode,
            'commentLineCharacter': comment,
            'fileEncoding': encoding,
            'skipRowsMode': skip_mode,
            'skipRows': skip_rows
        })

    def read_sql(self, data_source: MSSQLDataSource, query: str) -> 'Dataflow':
        """
        Adds step that can read data from an MS SQL database by executing the query specified.

        :param data_source: The details of the MS SQL database.
        :param query: The query to execute to read data.
        :return: A new Dataflow with Read SQL Step added.
        """
        return self.add_step('Database', {
            'server': data_source.server,
            'database': data_source.database,
            'credentialsType': data_source.credentials_type,
            'credentials': {
                'userName': data_source.user_name,
                'password': data_source.password
            },
            'query': query,
            'trustServer': data_source.trust_server,
            'databaseType': data_source.database_type
        })

    def read_postgresql(self, data_source: PostgreSQLDataSource, query: str) -> 'Dataflow':
        """
        Adds step that can read data from a PostgreSQL database by executing the query specified.

        :param data_source: The details of the PostgreSQL database.
        :param query: The query to execute to read data.
        :return: A new Dataflow with Read SQL Step added.
        """
        return self.add_step('Database', {
            'server': data_source.server,
            'database': data_source.database,
            'credentialsType': data_source.credentials_type,
            'credentials': {
                'userName': data_source.user_name,
                'password': data_source.password
            },
            'query': query,
            'databaseType': data_source.database_type
         })


    def read_parquet_file(self) -> 'Dataflow':
        """
        Adds step to parse Parquet files.

        :return: A new Dataflow with Parse Parquet File Step added.
        """
        return self.add_step('Microsoft.DPrep.ReadParquetFileBlock', {})

    def read_excel(self,
                   sheet_name: Optional[str] = None,
                   use_column_headers: bool = False,
                   skip_rows: int = 0) -> 'Dataflow':
        """
        Adds step to read and parse Excel files.

        :param sheet_name: The name of the sheet to load. The first sheet is loaded if none is provided.
        :param use_column_headers: Whether to use the first row as column headers.
        :param skip_rows: Number of rows to skip when loading the data.
        :return: A new Dataflow with Read Excel Step added.
        """
        return self.add_step('Microsoft.DPrep.ReadExcelBlock', {
                               'sheetName': sheet_name,
                               'useColumnHeaders': use_column_headers,
                               'skipRows': skip_rows
                            })

    def read_json(self,
                  json_extract_program: str,
                  encoding: FileEncoding):
        """
        Creates a new Dataflow with the operations required to read JSON files.

        :param json_extract_program: PROSE program that will be used to parse JSON.
        :param encoding: The encoding of the files being read.
        :return: A new Dataflow with Read JSON Step added.
        """
        return self.add_step('JSONFile', {
            'dsl': json_extract_program,
            'fileEncoding': encoding
        })

    TypeConversionInfo = TypeVar('TypeConversionInfo',
                                 FieldType,
                                 TypeConverter,
                                 Tuple[FieldType, List[str], Tuple[FieldType, str]])

    def set_column_types(self, type_conversions: Dict[str, TypeConversionInfo]) -> 'Dataflow':
        """
        Converts values in specified columns to the corresponding data types.

        .. remarks::

            The values in the type_conversions dictionary could be of several types:

            * :class:`azureml.dataprep.FieldType`
            * :class:`azureml.dataprep.TypeConverter`
            * Tuple of :class:`azureml.dataprep.FieldType`.DATE and List of format strings (single format string is also supported)

            .. code-block:: python

                import azureml.dataprep as dprep

                dataflow = dprep.read_csv(path='./some/path')
                dataflow = dataflow.set_column_types({'MyNumericColumn': dprep.FieldType.DECIMAL,
                                                   'MyBoolColumn': dprep.FieldType.BOOLEAN,
                                                   'MyAutodetectDateColumn': dprep.FieldType.DATE,
                                                   'MyDateColumnWithFormat': (dprep.FieldType.DATE, ['%m-%d-%Y']),
                                                   'MyOtherDateColumn': dprep.DateTimeConverter(['%d-%m-%Y'])})

            .. note::

                If you choose to convert a column to :class:`azureml.dataprep.FieldType`.DATE and do not provide \
                **format(s)** to use, DataPrep will attempt to infer a format to use by pulling on the data. \
                If a format could be inferred from the data, it will be used to convert values in the corresponding
                column. However, if a format could not be inferred, this step will fail and you will need to either \
                provide the format to use or use the interactive builder \
                :class:`azureml.dataprep.api.builders.ColumnTypesBuilder` by calling \
                'dataflow.builders.set_column_types()'

        :param type_conversions: A dictionary where key is column name and value is either
            :class:`azureml.dataprep.FieldType` or :class:`azureml.dataprep.TypeConverter` or a Tuple of
            :class:`azureml.dataprep.FieldType`.DATE and List of format strings

        :return: The modified Dataflow.
        """

        def _get_type_arguments(converter: TypeConverter):
            if not isinstance(converter, DateTimeConverter):
                return None

            return {'dateTimeFormats': converter.formats}

        def _are_all_date_formats_available(conversions: List[Any]) -> bool:
            for conversion in conversions:
                if conversion['typeProperty'] == FieldType.DATE or conversion['typeProperty'] == FieldType.DATE.value:
                    if conversion.get('typeArguments') is None \
                            or conversion['typeArguments']['dateTimeFormats'] is None \
                            or len(conversion['typeArguments']['dateTimeFormats']) == 0:
                        return False

            return True

        # normalize type_conversion argument
        for col in type_conversions.keys():
            conv_info = type_conversions.get(col)
            if not isinstance(conv_info, TypeConverter):
                # if a 2 value tuple and first value is FieldType.Date
                if isinstance(conv_info, tuple) and conv_info[0] == FieldType.DATE and len(conv_info) == 2:
                    type_conversions[col] = DateTimeConverter(conv_info[1] if isinstance(conv_info[1], List)
                                                              else [conv_info[1]])
                elif conv_info in FieldType:
                    type_conversions[col] = TypeConverter(conv_info)
                else:
                    raise ValueError('Unexpected conversion info for column: ' + col)

        # construct block arguments
        arguments = {'columnConversion': [{
            'column': ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN,
                                      details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(col))),
            'typeProperty': converter.data_type,
            'typeArguments': _get_type_arguments(converter)
        } for col, converter in type_conversions.items()]}

        need_to_learn = not _are_all_date_formats_available(arguments['columnConversion'])

        if need_to_learn:
            block_args = BlockArguments(PropertyValues.from_pod(arguments), 'Microsoft.DPrep.SetColumnTypesBlock')
            blocks = steps_to_block_datas(self._get_steps())
            set_column_types_block = self._engine_api.add_block_to_list(
                AddBlockToListMessageArguments(blocks=blocks,
                                               new_block_arguments=block_args))
            learned_arguments = set_column_types_block.arguments.to_pod()
            success = _are_all_date_formats_available(learned_arguments['columnConversion'])
            if not success:
                raise ValueError('Can\'t detect date_time_formats automatically, please provide desired formats.')

            arguments = learned_arguments

        return self.add_step('Microsoft.DPrep.SetColumnTypesBlock', arguments)

    def take_sample(self,
                    probability: float,
                    seed: Optional[int] = None) -> 'Dataflow':
        """
        Takes a random sample of the available records.

        :param probability: The probability of a record being included in the sample.
        :param seed: The seed to use for the random generator.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.TakeSampleBlock', {
            'probability': probability,
            'seed': seed or random.randint(0, 4294967295)
        })

    def take_stratified_sample(self,
                               columns: MultiColumnSelection,
                               fractions: Dict[Tuple, int],
                               seed: Optional[int] = None) -> 'Dataflow':
        """
        Takes a random stratified sample of the available records according to input fractions.

        :param columns: The strata columns.
        :param fractions: The strata to strata weights.
        :param seed: The seed to use for the random generator.
        :return: The modified Dataflow.
        """
        _fractions = []
        for stratum, weight in fractions.items():
            stratum_weight = {}
            stratum_as_any = []
            for column_val in stratum:
                _key = self._get_field_type(column_val).name.lower()
                _val = self._ticks(column_val) if isinstance(column_val, datetime.datetime) else column_val
                stratum_as_any.append({'{}'.format(_key): _val})
            stratum_weight['stratum'] = stratum_as_any
            stratum_weight['weight'] = weight
            _fractions.append(stratum_weight)
        return self.add_step('Microsoft.DPrep.TakeStratifiedSampleBlock', {
            'seed': seed or random.randint(0, 4294967295),
            'columns': column_selection_to_selector_value(columns),
            'fractions': _fractions
        })

    def filter(self, expression: Expression) -> 'Dataflow':
        """
        Filters the data, leaving only the records that match the specified expression.

        .. remarks::

            Expressions are started by indexing the Dataflow with the name of a column. They support a variety of
                functions and operators and can be combined using logical operators. The resulting expression will be
                lazily evaluated for each record when a data pull occurs and not where it is defined.

            .. code-block:: python

                dataflow['myColumn'] > dataflow['columnToCompareAgainst']
                dataflow['myColumn'].starts_with('prefix')

        :param expression: The expression to evaluate.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ExpressionFilterBlock', {'expression': expression.underlying_data})

    def add_column(self, expression: Expression, new_column_name: str, prior_column: str) -> 'Dataflow':
        """
        Adds a new column to the dataset. The values in the new column will be the result of invoking the specified
        expression.

        .. remarks::

            Expressions are built using the expression builders in the expressions module and the functions in
            the functions module. The resulting expression will be lazily evaluated for each record when a data pull
            occurs and not where it is defined.

        :param expression: The expression to evaluate to generate the values in the column.
        :param new_column_name: The name of the new column.
        :param prior_column: The name of the column after which the new column should be added. The default is to add the new column as the last column.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ExpressionAddColumnBlock', {
            'expression': expression.underlying_data,
            'newColumnName': new_column_name,
            'priorColumn': single_column_to_selector_value(prior_column) if prior_column is not None else None
        })

    ExampleData = TypeVar('ExampleData', Tuple[str, str], Tuple[Dict[str, str], str], List[Tuple[str, str]],
                          List[Tuple[Dict[str, str], str]])
    SourceColumns = TypeVar('SourceColumns', str, List[str])

    def derive_column_by_example(self,
                                 source_columns: SourceColumns,
                                 new_column_name: str,
                                 example_data: ExampleData) -> 'Dataflow':
        """
        Inserts a column by learning a program based on a set of source columns and provided examples.
            Dataprep will attempt to achieve the intended derivation inferred from provided examples.

        .. remarks::

            If you need more control of examples and generated program, create DeriveColumnByExampleBuilder instead.

        :param source_columns: Names of the columns from which the new column will be derived.
        :param new_column_name: Name of the new column to add.
        :param example_data: Examples to use as input for program generation.
            In case there is only one column to be used as source, examples could be Tuples of source value and intended
            target value. For example, you can have "example_data=[("2013-08-22", "Thursday"), ("2013-11-03", "Sunday")]".
            When multiple columns should be considered as source, each example should be a Tuple of dict-like sources
            and intended target value, where sources have column names as keys and column values as values.
        :return: The modified Dataflow.
        """

        if isinstance(source_columns, str):
            # for single source column case create a list for uniform processing
            source_columns = [source_columns]
        else:
            try:
                source_columns = [s for s in source_columns]
            except TypeError:
                source_columns = []

        if len(source_columns) == 0:
            raise ValueError('Please provide columns to derive from')

        if not isinstance(example_data, List):
            # for single example case create a list for uniform processing
            example_data = [example_data]

        source_data_and_examples = []
        for example_data_entry in example_data:
            if not isinstance(example_data_entry[1], str):
                raise ValueError('Incorrect example data. "example_data" should be either '
                                 'Tuple[str|Dict[str, str], str], or List[Tuple[str|Dict[str, str], str]]')
            if isinstance(example_data_entry[0], Dict):
                source_data_and_examples.append(example_data_entry)
            elif len(source_columns) == 1:
                source_data_and_examples.append((
                    {source_columns[0]: str(example_data_entry[0])},
                    example_data_entry[1]))
            else:
                raise ValueError('Incorrect example data. When you derive from multiple columns "example_data" should '
                                 'be either Tuple[Dict[str, str], str] or List[Tuple[Dict[str, str], str]]')

        derive_column_builder = self.builders.derive_column_by_example(source_columns, new_column_name)

        for item in source_data_and_examples:
            derive_column_builder.add_example(source_data=item[0], example_value=item[1])

        return derive_column_builder.to_dataflow()

    def fuzzy_group_column(self,
                           source_column: str,
                           new_column_name: str,
                           similarity_threshold: float = 0.8,
                           similarity_score_column_name: str = None) -> 'Dataflow':
        """
        Add a column where similar values from the source column are fuzzy-grouped to their canonical form.

        .. remarks::

            This method will cluster similar values automatically.
            This is useful when working with data gathered from multiple sources or through human input,
            where the same entities are often represented by multiple values due to different spellings, varying capitalizations, or abbreviations.
            For example, you may have a column with values Chicago, CHICAGO, SEATTLE, Seattle, St. Louis, St. Lois, ST LOUIS, and you want to redeuce them to the distinct values - Chicago, Seattle and St. Louis.
            If you need more control of grouping, create FuzzyGroupBuilder instead.

        :param source_column: Column with values to group.
        :param new_column_name: Name of the new column to add.
        :param similarity_threshold: Similarity between values to be grouped together.
        :param similarity_score_column_name: If provided, this transform will also add a column with calculated
            similarity score between every pair of original and canonical values. This information is helpful to determine `similarity_threshold`.
        :return: The modified Dataflow.
        """
        builder = self.builders.fuzzy_group_column(source_column,
                                                   new_column_name,
                                                   similarity_threshold,
                                                   similarity_score_column_name)
        return builder.to_dataflow()

    def one_hot_encode(self, source_column: str, prefix: str = None) -> 'Dataflow':
        """
        Adds a binary column for each categorical label from the source column values. For more control over categorical
            labels, use OneHotEncodingBuilder.

        :param source_column: Column name from which categorical labels will be generated.
        :param prefix: An optional prefix to use for the new columns.
        :return: The modified Dataflow.
        """
        builder = self.builders.one_hot_encode(source_column, prefix)
        return builder.to_dataflow()

    def label_encode(self, source_column: str, new_column_name: str) -> 'Dataflow':
        """
        Adds a column with encoded labels generated from the source column. For explicit label encoding,
            use LabelEncoderBuilder.

        :param source_column: Column name from which encoded labels will be generated.
        :param new_column_name: The new column's name.
        :return: The modified Dataflow.
        """
        builder = self.builders.label_encode(source_column, new_column_name)
        return builder.to_dataflow()

    def pivot(self,
              columns_to_pivot: List[str],
              value_column: str,
              summary_function: SummaryFunction = None,
              group_by_columns: List[str] = None,
              null_value_replacement: str = None,
              error_value_replacement: str= None) -> 'Dataflow':
        """
        Returns a new Dataflow with columns generated from the values in the selected columns to pivot.

        .. remarks::

            The values of the new dataflow come from the value column selected.
            Additionally there is an optional summarization that consists of an aggregation and a group by.

        :param columns_to_pivot: The columns used to get the values from which the new dataflow's new columns are generated.
        :param value_column: The column used to get the values that will populate the new dataflow's rows.
        :summary_function: The summary function used to aggregate the values.
        :group_by_columns: The columns used to group the new dataflow rows.
        :null_value_replacement: String value to replace null values in columns_to_pivot. If unspecified, the string "NULL" will be used.
        :error_value_replacement: String value to replace error values in columns_to_pivot. If unspecified, the string "ERROR" will be used.
        """
        builder = self.builders.pivot(columns_to_pivot,
                                      value_column,
                                      summary_function,
                                      group_by_columns,
                                      null_value_replacement,
                                      error_value_replacement)
        return builder.to_dataflow()

    def quantile_transform(self, source_column: str, new_column: str,
                           quantiles_count: int = 1000, output_distribution: str = 'Uniform'):
        """
        Perform quantile transformation to the source_column and output the transformed result in new_column.

        :param source_column: The column which quantile transform will be applied to.
        :param new_column: The column where the transformed data will be placed.
        :param quantiles_count: The number of quantiles used. This will be used to discretize the cdf, defaults to 1000
        :param output_distribution: The distribution of the transformed data, defaults to 'Uniform'
        :return: The modified Dataflow.
        """
        return self.builders \
            .quantile_transform(source_column, new_column, quantiles_count, output_distribution) \
            .to_dataflow()

    def min_max_scale(self,
                      column: str,
                      range_min: float = 0,
                      range_max: float = 1,
                      data_min: float = None,
                      data_max: float = None) -> 'Dataflow':
        """
        Scales the values in the specified column to lie within range_min (default=0) and range_max (default=1).

        :param column: The column to scale.
        :param range_min: Desired min of scaled values.
        :param range_max: Desired max of scaled values.
        :param data_min: Min of source column. If not provided, a scan of the data will be performed to find the min.
        :param data_max: Max of source column. If not provided, a scan of the data will be performed to find the max.
        :return: The modified Dataflow.
        """
        builder = self.builders.min_max_scale(column, range_min, range_max, data_min, data_max)
        return builder.to_dataflow()

    def random_split(self,
                     percentage: float,
                     seed: Optional[int] = None) -> ('Dataflow', 'Dataflow'):
        """
        Returns two Dataflows from the original Dataflow, with records randomly and approximately split by the percentage
            specified (using a seed). If the percentage specified is p (where p is between 0 and 1), the first returned dataflow
            will contain approximately p*100% records from the original dataflow, and the second dataflow will contain all the
            remaining records that were not included in the first. A random seed will be used if none is provided.

        :param percentage: The approximate percentage to split the Dataflow by. This must be a number between 0.0 and 1.0.
        :param seed: The seed to use for the random split.
        :return: Two Dataflows containing records randomly split from the original Dataflow. If the percentage specified is p,
            the first dataflow contains approximately p*100% of the records from the original dataflow.

        """
        if percentage < 0.0 or percentage > 1.0:
            raise ValueError("percentage must be a number between 0.0 and 1.0.")

        dflow_1 = self.add_step('Microsoft.DPrep.RandomSplitBlock', {
            'probability': percentage,
            'seed': seed or random.randint(0, 4294967295)
        })

        dflow_2 = Dataflow(self._engine_api)
        reference = make_activity_reference(dflow_1)
        reference.referenced_step = dflow_1._get_steps()[-1]
        dflow_2 = dflow_2.add_step('Microsoft.DPrep.ReferenceAndInverseSplitBlock', {
            'sourceFilter': reference
        })

        return dflow_1, dflow_2

    def replace_datasource(self, new_datasource: DataSource) -> 'Dataflow':
        """
        Returns new Dataflow with its DataSource replaced by the given one.

        .. remarks::

            The given 'new_datasource' must match the type of datasource already in the Dataflow.
            For example a MSSQLDataSource cannot be replaced with a FileDataSource.

        :param new_datasource: DataSource to substitute into new Dataflow.
        :return: The modified Dataflow.
        """
        if isinstance(new_datasource, MSSQLDataSource):
            if not self._steps[0].step_type == 'Database':
                raise ValueError("Can't replace '" + self._steps[0].step_type + "' Datasource with MSSQLDataSource.")
            from .readers import read_sql
            new_datasource_step = read_sql(new_datasource, self._steps[0].arguments['query'])._get_steps()[0]
            new_datasource_step.id = self._steps[0].id
        else:
            if self._steps[0].step_type == 'Database':
                raise ValueError("Can only replace 'Database' Datasource with MSSQLDataSource.")
            import copy
            new_datasource_step = copy.deepcopy(self._steps[0])
            new_datasource_step.arguments['path'] = new_datasource.underlying_value
        return Dataflow(self._engine_api, [new_datasource_step] + self._steps[1:])

    def replace_reference(self, new_reference: DataflowReference) -> 'Dataflow':
        """
        Returns new Dataflow with its reference DataSource replaced by the given one.

        :param new_reference: Reference to be substituted for current Reference in Dataflow.
        :return: The modified Dataflow.
        """
        if self._steps[0].step_type != 'Microsoft.DPrep.ReferenceBlock':
            raise ValueError("Can only replace 'Reference' Datasource with 'DataflowReference', found: " +
                             self._steps[0].step_type)
        new_reference_step = Dataflow.reference(new_reference)._get_steps()[0]
        new_reference_step.id = self._steps[0].id
        return Dataflow(self._engine_api, [new_reference_step] + self._steps[1:])

    def cache(self, directory_path: str) -> 'Dataflow':
        """
        Pulls all the records from this Dataflow and cache the result to disk.

        .. remarks::

            This is very useful when data is accessed repeatedly, as future executions will reuse
            the cached result without pulling the same Dataflow again.

        :param directory_path: The directory to save cache files.
        :return: The modified Dataflow.
        """
        df = self.add_step('Microsoft.DPrep.CacheBlock', {
            'cachePath': LocalDataSource(directory_path).underlying_value
        })
        df.head(1)
        return df

    def new_script_column(self,
                          new_column_name: str,
                          insert_after: str,
                          script: str) -> 'Dataflow':
        """
        Adds a new column to the Dataflow using the passed in Python script.

        .. remarks::

            The Python script must define a function called newvalue that takes a single argument, typically
                called row. The row argument is a dict (key is column name, value is current value) and will be passed
                to this function for each row in the dataset. This function must return a value to be used in the new column.

            .. note::

                Any libraries that the Python script imports must exist in the environment where the dataflow is run.

            .. code-block:: python

                import numpy as np
                def newvalue(row):
                    return np.log(row['Metric'])

        :param new_column_name: The name of the new column being created.
        :param insert_after: The column after which the new column will be inserted.
        :param script: The script that will be used to create this new column.
        :return: The modified Dataflow.
        """
        return self.add_step(step_type='Microsoft.DPrep.AddCustomColumnBlock', arguments={
            "codeBlockType": CodeBlockType.MODULE,
            "columnId": new_column_name,
            "customExpression": script,
            "priorColumnId": ColumnsSelector(
                                type=ColumnsSelectorType.SINGLECOLUMN,
                                details=cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(insert_after)))
          })

    def new_script_filter(self, script: str) -> 'Dataflow':
        """
        Filters the Dataflow using the passed in Python script.

        .. remarks::

            The Python script must define a function called includerow that takes a single argument, typically
                called row. The row argument is a dict (key is column name, value is current value) and will be passed
                to this function for each row in the dataset. This function must return True or False depending on whether
                the row should be included in the dataflow. Any libraries that the Python script imports must exist in the
                environment where the dataflow is run.

            .. code-block:: python

                def includerow(row):
                    return row['Metric'] > 100

        :param script: The script that will be used to filter the dataflow.
        :return: The modified Dataflow.
        """
        return self.add_step(step_type='Microsoft.DPrep.FilterBlock', arguments={
            "codeBlockType": CodeBlockType.MODULE,
            "filterExpression": script
          })

    def transform_partition(self,
                            script: str) -> 'Dataflow':
        """
        Transforms an entire partition using the passed in Python script.

        .. remarks::

            The Python script must define a function called transform that takes two arguments, typically called `df` and
                `index`. The `df` argument will be a Pandas Dataframe passed to this function that contains the data for the
                partition and the `index` argument is a unique identifier of the partition.

            .. note::

                `df` does not usually contain all of the data in the dataflow, but a partition of the data as it is being processed in the \
                runtime. The number and contents of each partition is not guaranteed across runs.
            The transform function can fully edit the passed in dataframe or even create a new one, but must return a
                dataframe. Any libraries that the Python script imports must exist in the environment where the dataflow
                is run.

            .. code-block:: python

                # the script passed in should have this function defined
                def transform(df, index):
                    # perform any partition level transforms here and return resulting `df`
                    return df

        :param script: The script that will be used to transform the partition.
        :return: The modified Dataflow.
        """
        return self.add_step(step_type='Microsoft.DPrep.MapPartitionsAsDataFrameBlock', arguments={
            "codeBlockType": CodeBlockType.MODULE,
            "MapPartitionsAsDataFrameBlock": script
          })

    def transform_partition_with_file(self,
                                      script_path: str) -> 'Dataflow':
        """
        Transforms an entire partition using the Python script in the passed in file.

        .. remarks::

            The Python script must define a function called transform that takes two arguments, typically called `df` and
                `index`. The first argument `df` will be a Pandas Dataframe that contains the data for the partition and the
                second argument `index` will be a unique identifier for the partition.

            .. note::

                `df` does not usually contain all of the data in the dataflow, but a partition of the data as it is being processed in the runtime.\
                The number and contents of each partition is not guaranteed across runs.

            The transform function can fully edit the passed in dataframe or even create a new one, but must return a
                dataframe. Any libraries that the Python script imports must exist in the environment where the dataflow is run.

            .. code-block:: python

                # the script file passed in should have this function defined
                def transform(df, index):
                    # perform any partition level transforms here and return resulting `df`
                    return df

        :param script_path: Relative path to script that will be used to transform the partition.
        :return: The modified Dataflow.
        """
        return self.add_step(step_type='Microsoft.DPrep.MapPartitionsAsDataFrameBlock', arguments={
            "codeBlockType": CodeBlockType.FILE,
            "MapPartitionsAsDataFrameBlock": script_path
        })

    def split_column_by_delimiters(self,
                                   source_column: str,
                                   delimiters: Delimiters,
                                   keep_delimiters: False) -> 'Dataflow':
        """
        Splits the provided column and adds the resulting columns to the dataflow.

        .. remarks::

            This will pull small sample of the data, determine number of columns it should expect as a result of the
                split and generate a split program that would ensure that the expected number of columns will be produced,
                so that there is a deterministic schema after this operation.

        :param source_column: Column to split.
        :param delimiters: String or list of strings to be deemed as column delimiters.
        :param keep_delimiters: Controls whether to keep or drop column with delimiters.
        :return: The modified Dataflow.
        """
        builder = self.builders.split_column_by_example(source_column=source_column,
                                                        delimiters=delimiters,
                                                        keep_delimiters=keep_delimiters)
        return builder.to_dataflow()

    def split_column_by_example(self, source_column: str, example: SplitExample = None) -> 'Dataflow':
        """
        Splits the provided column and adds the resulting columns to the dataflow based on the provided example.

        .. remarks::

            This will pull small sample of the data, determine the best program to satisfy provided example
                and generate a split program that would ensure that the expected number of columns will be produced, so that
                there is a deterministic schema after this operation.

            .. note::

                If example is not provided, this will generate a split program based on common split patterns, like splitting by space, punctuation, date parts and etc.

        :param source_column: Column to split.
        :param example: Example to use for program generation.
        :return: The modified Dataflow.
        """
        builder = self.builders.split_column_by_example(source_column=source_column)
        if example is not None:
            builder.add_example(example)
        return builder.to_dataflow()

    def replace(self,
                columns: MultiColumnSelection,
                find: Any,
                replace_with: Any) -> 'Dataflow':
        """
        Replaces values in a column that match the specified search value.

        .. remarks::

            The following types are supported for both the find or replace arguments: str, int, float,
                datetime.datetime, and bool.

        :param columns: The source columns.
        :param find: The value to find, or None.
        :param replace_with: The replacement value, or None.
        :return: The modified Dataflow.
        """
        replace_dict = self._make_replace_dict(find, replace_with)

        if replace_dict['valueToFindType'] == FieldType.UNKNOWN:
            raise ValueError('The type of the find argument is not supported')
        if replace_dict['replaceWithType'] == FieldType.UNKNOWN:
            raise ValueError('The type of the replace_with argument is not supported')

        return self._add_replace_step(columns, replace_dict)

    def error(self,
              columns: MultiColumnSelection,
              find: Any,
              error_code: str) -> 'Dataflow':
        """
        Creates errors in a column for values that match the specified search value.

        .. remarks::

            The following types are supported for the find argument: str, int, float,
                datetime.datetime, and bool.

        :param columns: The source columns.
        :param find: The value to find, or None.
        :param error_code: The error code to use in new errors, or None.
        :return: The modified Dataflow.
        """
        replace_dict = self._make_replace_dict(find, None)

        if replace_dict['valueToFindType'] == FieldType.UNKNOWN:
            raise ValueError('The type of the find argument is not supported')
        replace_dict['replaceWithType'] = FieldType.ERROR

        return self._add_replace_step(columns, replace_dict, error_code)

    def fill_nulls(self,
                   columns: MultiColumnSelection,
                   fill_with: Any) -> 'Dataflow':
        """
        Fills all nulls in a column with the specified value.

        .. remarks::

            The following types are supported for the fill_with argument: str, int, float,
                datetime.datetime, and bool.

        :param columns: The source columns.
        :param fill_with: The value to fill nulls with.
        :return: The modified Dataflow.
        """
        replace_dict = self._make_replace_dict(None, fill_with)

        if replace_dict['replaceWithType'] == FieldType.UNKNOWN or replace_dict['replaceWithType'] == FieldType.NULL:
            raise ValueError('The type of the fill_with argument is not supported')

        return self.add_step('Microsoft.DPrep.FillNullsBlock', {
            'columns': column_selection_to_selector_value(columns),
            'replaceWithType': replace_dict['replaceWithType'],
            'stringReplaceWith': replace_dict['stringReplaceWith'],
            'doubleReplaceWith': replace_dict['doubleReplaceWith'],
            'datetimeReplaceWith': replace_dict['datetimeReplaceWith'],
            'booleanReplaceWith': replace_dict['booleanReplaceWith']
        })

    def fill_errors(self,
                    columns: MultiColumnSelection,
                    fill_with: Any) -> 'Dataflow':
        """
        Fills all errors in a column with the specified value.

        .. remarks::

            The following types are supported for the fill_with argument: str, int, float,
                datetime.datetime, and bool.

        :param columns: The source columns.
        :param fill_with: The value to fill errors with, or None.
        :return: The modified Dataflow.
        """
        replace_dict = self._make_replace_dict(None, fill_with)

        replace_dict['valueToFindType'] = FieldType.ERROR
        if replace_dict['replaceWithType'] == FieldType.UNKNOWN:
            raise ValueError('The type of the fill_with argument is not supported')

        return self._add_replace_step(columns, replace_dict)

    def join(self,
             right_dataflow: DataflowReference,
             join_key_pairs: List[Tuple[str, str]] = None,
             join_type: JoinType = JoinType.MATCH,
             left_column_prefix: str = 'l_',
             right_column_prefix: str = 'r_',
             left_non_prefixed_columns: List[str] = None,
             right_non_prefixed_columns: List[str] = None) -> 'Dataflow':
        """
        Creates a new Dataflow that is a result of joining this Dataflow with the provided right_dataflow.

        :param right_dataflow: Right Dataflow or DataflowReference to join with.
        :param join_key_pairs: Key column pairs. List of tuples of columns names where each tuple forms a key pair to
            join on. For instance: [('column_from_left_dataflow', 'column_from_right_dataflow')]
        :param join_type: Type of join to perform. Match is default.
        :param left_column_prefix: Prefix to use in result Dataflow for columns originating from left_dataflow.
            Needed to avoid column name conflicts at runtime.
        :param right_column_prefix: Prefix to use in result Dataflow for columns originating from right_dataflow.
            Needed to avoid column name conflicts at runtime.
        :param left_non_prefixed_columns: List of column names from left_dataflow that should not be prefixed with
            left_column_prefix. Every other column appearing in the data at runtime will be prefixed.
        :param right_non_prefixed_columns: List of column names from right_dataflow that should not be prefixed with
            left_column_prefix. Every other column appearing in the data at runtime will be prefixed.
        :return: The new Dataflow.
        """

        return Dataflow.join(self,
                             right_dataflow,
                             join_key_pairs,
                             join_type,
                             left_column_prefix,
                             right_column_prefix,
                             left_non_prefixed_columns,
                             right_non_prefixed_columns)

    def write_to_csv(self,
                     directory_path: DataDestination,
                     separator: str = ',',
                     na: str = 'NA',
                     error: str = 'ERROR') -> 'Dataflow':
        """
        Write out the data in the Dataflow in a delimited text format. The output is specified as a directory
            which will contain multiple files, one per partition processed in the Dataflow.

        :param directory_path: The path to a directory in which to store the output files.
        :param separator: The separator to use.
        :param na: String to use for null values.
        :param error: String to use for error values.
        :return: The modified Dataflow. Every execution of the returned Dataflow will perform the write again.
        """
        if isinstance(directory_path, str):
            directory_path = FileOutput.file_output_from_str(directory_path)

        if isinstance(directory_path, FileOutput):
            return self.add_step('Microsoft.DPrep.WriteToCsvBlock', {
                'filePath': None,
                'directoryPath': directory_path.underlying_value,
                'separator': separator,
                'singleFile': False,
                'na': na,
                'error': error
            })
        return self.add_step('Microsoft.DPrep.WriteCsvToDatastoreBlock', {
            'datastore': get_datastore_value(directory_path)[1]._to_pod(),
            'separator': separator,
            'singleFile': False,
            'na': na,
            'error': error
        })

    def write_to_parquet(self,
                         file_path: Optional[DataDestination] = None,
                         directory_path: Optional[DataDestination] = None,
                         single_file: bool = False,
                         error: str = 'ERROR',
                         row_groups: int = 0) -> 'Dataflow':
        """
        Writes out the data in the Dataflow into Parquet files.

        :param file_path: The path in which to store the output file.
        :param directory_path: The path in which to store the output files.
        :param single_file: Whether to store the entire Dataflow in a single file.
        :param error: String to use for error values.
        :param row_groups: Number of rows to use per row group.
        :return: The modified Dataflow.
        """
        if directory_path and isinstance(directory_path, str):
            directory_path = FileOutput.file_output_from_str(directory_path)
        if file_path and isinstance(file_path, str):
            file_path = FileOutput.file_output_from_str(file_path)

        if isinstance(directory_path, FileOutput) or isinstance(file_path, FileOutput):
            return self.add_step('Microsoft.DPrep.WriteToParquetBlock', {
                'filePath': file_path.underlying_value if file_path is not None else None,
                'directoryPath': directory_path.underlying_value if directory_path is not None else None,
                'singleFile': single_file,
                'error': error,
                'rowGroups': row_groups
            })
        return self.add_step(
            'Microsoft.DPrep.WriteParquetToDatastoreBlock', {
                'datastore': get_datastore_value(directory_path if directory_path else file_path)[1]._to_pod(),
                'singleFile': single_file,
                'error': error,
                'rowGroups': row_groups
            }
        )

    SortColumns = TypeVar('SortColumns', str, List[str])

    def sort_asc(self, columns: SortColumns) -> 'Dataflow':
        """
        Sorts the dataset in ascending order by the specified columns.

        :param columns: The columns to sort in ascending order.
        :return: The modified Dataflow.
        """
        columns = [columns] if not isinstance(columns, List) else columns
        return self.add_step('Microsoft.DPrep.SortBlock', {
            'sortOrder': [{'column': single_column_to_selector_value(c), 'descending': False} for c in columns]
        })

    def sort_desc(self, columns: SortColumns) -> 'Dataflow':
        """
        Sorts the dataset in descending order by the specified columns.

        :param columns: The columns to sort in descending order.
        :return: The modified Dataflow.
        """
        columns = [columns] if not isinstance(columns, List) else columns
        return self.add_step('Microsoft.DPrep.SortBlock', {
            'sortOrder': [{'column': single_column_to_selector_value(c), 'descending': True} for c in columns]
        })

    def to_datetime(self,
                    columns: MultiColumnSelection,
                    date_time_formats: Optional[List[str]] = None,
                    date_constant: Optional[str] = None) -> 'Dataflow':
        """
        Converts the values in the specified columns to DateTimes.

        :param columns: The source columns.
        :param date_time_formats: The formats to use to parse the values. If none are provided, a partial scan of the
            data will be performed to derive one.
        :param date_constant: If the column contains only time values, a date to apply to the resulting DateTime.
        :return: The modified Dataflow.
        """
        arguments = {
            'columns': column_selection_to_selector_value(columns),
            'dateTimeFormats': [p for p in date_time_formats] if date_time_formats is not None else None,
            'dateConstant': date_constant
        }

        if date_time_formats is None or len(date_time_formats) == 0:
            blocks = steps_to_block_datas(self._get_steps())
            block_args = BlockArguments(PropertyValues.from_pod(arguments), 'Microsoft.DPrep.ToDateTimeBlock')
            to_datetime_block = self._engine_api.add_block_to_list(
                AddBlockToListMessageArguments(blocks=blocks, new_block_arguments=block_args))
            learned_arguments = to_datetime_block.arguments.to_pod()
            if learned_arguments.get('dateTimeFormats') is None or len(learned_arguments['dateTimeFormats']) == 0:
                raise ValueError('Can\'t detect date_time_formats automatically, please provide desired formats.')

            arguments['dateTimeFormats'] = learned_arguments['dateTimeFormats']

        return self.add_step('Microsoft.DPrep.ToDateTimeBlock', arguments)

    def summarize(self,
                  summary_columns: Optional[List[SummaryColumnsValue]] = None,
                  group_by_columns: Optional[List[str]] = None,
                  join_back: bool = False,
                  join_back_columns_prefix: Optional[str] = None) -> 'Dataflow':
        """
        Summarizes data by running aggregate functions over specific columns.

        .. remarks::

            The aggregate functions are independent and it is possible to aggregate the same column multiple times.
                Unique names have to be provided for the resulting columns. The aggregations can be grouped, in which case
                one record is returned per group; or ungrouped, in which case one record is returned for the whole dataset.
                Additionally, the results of the aggregations can either replace the current dataset or augment it by
                appending the result columns.

        :param summary_columns: List of :class:`SummaryColumnsValue` where each value defines column to summarize,
            summary function to use and name of resulting column to add.
        :param group_by_columns: Columns to group by.
        :param join_back: Whether to append subtotals or replace current data with them.
        :param join_back_columns_prefix: Prefix to use for subtotal columns when appending them to current data.
        :return: The modified Dataflow.
        """
        # handle string as a single column
        group_by_columns = [] if group_by_columns is None else\
            [group_by_columns] if isinstance(group_by_columns, str) else group_by_columns
        if not summary_columns and len(group_by_columns) == 0:
            raise ValueError("Missing required argument. Please provide at least one of the following arguments: "
                             "'summary_columns', 'group_by_columns'.")
        return self._summarize(summary_columns, group_by_columns, join_back, join_back_columns_prefix)

    def assert_value(self,
                     columns: MultiColumnSelection,
                     expression: Expression,
                     policy: AssertPolicy = AssertPolicy.ERRORVALUE,
                     error_code: str = 'AssertionFailed') -> 'Dataflow':
        """
        Ensures that values in the specified columns satisfy the provided expression. This is useful to identify anomalies in the dataset
            and avoid broken pipelines by handling assertion errors in a clean way.

        :param columns: Columns to apply evaluation to.
        :param expression: Expression that has to be evaluated to be True for the value to be kept.
        :param policy: Action to take when expression is evaluated to False. Options are `FAILEXECUTION` and `ERRORVALUE`.
            `FAILEXECUTION` ensures that any data that violates the assertion expression during execution will immediately fail the job. This is useful to save computing resources and time.
            `ERRORVALUE` captures any data that violates the assertion expression by replacing it with error_code. This allows you to handle these error values by either filtering or replacing them.
        :param error_code: Error message to use to replace values failing the assertion or failing an execution.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ExpressionAssertValueBlock', {
            'columns': column_selection_to_selector_value(columns),
            'expression': expression.underlying_data,
            'assertPolicy': policy,
            'errorCode': error_code
        })

    def get_missing_secrets(self) -> List[str]:
        """
        Get a list of missing secret IDs.

        :return: A list of missing secret IDs.
        """
        secrets = self._engine_api.get_secrets(GetSecretsMessageArguments(steps_to_block_datas(self._steps)))
        missing_secret_ids = map(
            lambda secret: secret.key,
            filter(lambda secret: not secret.is_available, secrets)
        )

        return list(missing_secret_ids)

    def use_secrets(self, secrets: Dict[str, str]):
        """
        Uses the passed in secrets for execution.

        :param secrets: A dictionary of secret ID to secret value. You can get the list of required secrets by calling
            the get_missing_secrets method on Dataflow.
        """
        self._engine_api.add_temporary_secrets(secrets)

    def _get_source_data_hash(self) -> str:
        """
        Get the hash of the source data in the dataflow
        """
        return self._engine_api.get_source_data_hash(GetSourceDataHashMessageArguments(
            blocks=steps_to_block_datas(self._steps)
        ))

    @staticmethod
    def get_files(path: FilePath) -> 'Dataflow':
        """
        Expands the path specified by reading globs and files in folders and outputs one record per file found.

        :param path: The path or paths to expand.
        :return: A new Dataflow.
        """
        return Dataflow._path_to_get_files_block(path)

    @staticmethod
    def open(file_path: str) -> 'Dataflow':
        """
        Opens a Dataflow with specified name from the package file.

        :param file_path: Path to the package containing the Dataflow.
        :return: The Dataflow.
        """
        activity_data = get_engine_api().get_activity(file_path)
        return Dataflow._dataflow_from_activity_data(activity_data, get_engine_api())

    @staticmethod
    def from_json(dataflow_json: str) -> 'Dataflow':
        """
        Load Dataflow from 'package_json'.

        :param dataflow_json: JSON string representation of the Package.
        :return: New Package object constructed from the JSON string.
        """
        engine_api = get_engine_api()
        activity_data = engine_api.load_activity_from_json(dataflow_json)
        return Dataflow._dataflow_from_activity_data(activity_data, get_engine_api())

    def save(self, file_path: str):
        """
        Saves the Dataflow to the specified file

        :param file_path: The path of the file.
        """
        activity_data = Dataflow._dataflow_to_anonymous_activity_data(self)
        self._engine_api.save_activity_from_data(SaveActivityFromDataMessageArguments(activity_data, file_path))

    def to_json(self) -> str:
        """
        Get the JSON string representation of the Dataflow.
        """
        return self._engine_api.save_activity_to_json(Dataflow._dataflow_to_anonymous_activity_data(self))

    @staticmethod
    def _dataflow_from_activity_data(activity_data: AnonymousActivityData, engine_api: EngineAPI) -> 'Dataflow':
        steps = [Dataflow._step_from_block_data(bd) for bd in activity_data.blocks]
        df = Dataflow(engine_api, steps)
        df._activity_data = activity_data
        return df

    @staticmethod
    def _dataflow_to_anonymous_activity_data(dataflow: 'Dataflow') -> AnonymousActivityData:
        return AnonymousActivityData(
            [AnonymousBlockData(step.arguments,
                                step.id,
                                step.local_data,
                                step.step_type) for step in dataflow._get_steps()]
        )

    @staticmethod
    def _step_from_block_data(block_data: AnonymousBlockData):
        step = Step(block_data.type, block_data.arguments.to_pod(), block_data.local_data.to_pod())
        step.id = block_data.id
        step._block_data = block_data
        return step

    @staticmethod
    def _path_to_get_files_block(path: FilePath, archive_options: ArchiveOptions = None) -> 'Dataflow':
        try:
            if _is_datapath(path) or _is_datapaths(path):
                return datastore_to_dataflow(path)
        except ImportError:
            pass

        datasource = path if isinstance(path, FileDataSource) else FileDataSource.datasource_from_str(path)
        return Dataflow._get_files(datasource, archive_options)

    @staticmethod
    def _get_files(path: FileDataSource, archive_options: ArchiveOptions = None) -> 'Dataflow':
        """
        Expands the path specified by reading globs and files in folders and outputs one record per file found.

        :param path: The path or paths to expand.
        :return: A new Dataflow.
        """
        df = Dataflow(get_engine_api())
        args = {
            'path': path.underlying_value
        }
        if archive_options is not None:
            args['isArchive'] = True
            args['archiveOptions'] = {
                'archiveType': archive_options.archive_type
            }
            if archive_options.entry_glob is not None:
                args['archiveOptions']['entryGlob'] = archive_options.entry_glob

        return df.add_step('Microsoft.DPrep.GetFilesBlock', args)

    @staticmethod
    def _datetime_for_message(dt: datetime):
        t = {'timestamp': int(dt.timestamp() * 1000)}
        return t

    @staticmethod
    def _ticks(dt: datetime):
        return int((dt - datetime.datetime(1, 1, 1)).total_seconds() * 10000000)

    @staticmethod
    def _get_field_type(data):
        if data is None:
            return ValueKind.NULL
        elif isinstance(data, str):
            return ValueKind.STRING
        elif isinstance(data, int):
            return ValueKind.LONG
        elif isinstance(data, float):
            return ValueKind.DOUBLE
        elif isinstance(data, datetime.datetime):
            return ValueKind.DATETIME
        elif isinstance(data, bool):
            return ValueKind.BOOLEAN

    def _set_values_to_find(self, replace_dict: Dict[str, Any], find: Any):
        if find is None:
            replace_dict['valueToFindType'] = FieldType.NULL
        elif isinstance(find, str):
            replace_dict['valueToFindType'] = FieldType.STRING
            replace_dict['stringValueToFind'] = find
        elif isinstance(find, int) or isinstance(find, float):
            replace_dict['valueToFindType'] = FieldType.DECIMAL
            replace_dict['doubleValueToFind'] = find
        elif isinstance(find, datetime.datetime):
            replace_dict['valueToFindType'] = FieldType.DATE
            replace_dict['datetimeValueToFind'] = self._datetime_for_message(find)
        elif isinstance(find, bool):
            replace_dict['valueToFindType'] = FieldType.BOOLEAN
            replace_dict['booleanValueToFind'] = find

    def _make_replace_dict(self, find: Any, replace_with: Any):
        replace_dict = {
            'valueToFindType': FieldType.UNKNOWN,
            'stringValueToFind': None,
            'doubleValueToFind': None,
            'datetimeValueToFind': None,
            'booleanValueToFind': None,
            'replaceWithType': FieldType.UNKNOWN,
            'stringReplaceWith': None,
            'doubleReplaceWith': None,
            'datetimeReplaceWith': None,
            'booleanReplaceWith': None
        }

        self._set_values_to_find(replace_dict, find)

        if replace_with is None:
            replace_dict['replaceWithType'] = FieldType.NULL
        elif isinstance(replace_with, str):
            replace_dict['replaceWithType'] = FieldType.STRING
            replace_dict['stringReplaceWith'] = replace_with
        elif isinstance(replace_with, int) or isinstance(replace_with, float):
            replace_dict['replaceWithType'] = FieldType.DECIMAL
            replace_dict['doubleReplaceWith'] = replace_with
        elif isinstance(replace_with, datetime.datetime):
            replace_dict['replaceWithType'] = FieldType.DATE
            replace_dict['datetimeReplaceWith'] = self._datetime_for_message(replace_with)
        elif isinstance(replace_with, bool):
            replace_dict['replaceWithType'] = FieldType.BOOLEAN
            replace_dict['booleanReplaceWith'] = replace_with

        return replace_dict

    def _add_replace_step(self, columns: MultiColumnSelection, replace_dict: Dict, error_replace_with: str = None):
        error_replace_with = str(error_replace_with) if error_replace_with is not None else None
        return self.add_step('Microsoft.DPrep.ReplaceBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'valueToFindType': replace_dict['valueToFindType'],
                                 'stringValueToFind': replace_dict['stringValueToFind'],
                                 'doubleValueToFind': replace_dict['doubleValueToFind'],
                                 'datetimeValueToFind': replace_dict['datetimeValueToFind'],
                                 'booleanValueToFind': replace_dict['booleanValueToFind'],
                                 'replaceWithType': replace_dict['replaceWithType'],
                                 'stringReplaceWith': replace_dict['stringReplaceWith'],
                                 'doubleReplaceWith': replace_dict['doubleReplaceWith'],
                                 'datetimeReplaceWith': replace_dict['datetimeReplaceWith'],
                                 'booleanReplaceWith': replace_dict['booleanReplaceWith'],
                                 'errorReplaceWith': error_replace_with
                             })

    def _raise_if_missing_secrets(self, secrets: Dict[str, str]=None):
        missing_secrets = set(self.get_missing_secrets())
        if len(missing_secrets) == 0:
            return

        new_secret_ids = set(secrets.keys()) if secrets else set()
        missing_secrets = missing_secrets.difference(new_secret_ids)

        if len(missing_secrets) == 0:
            return

        class MissingSecretsError(Exception):
            def __init__(self, missing_secret_ids):
                super().__init__(
                    'Required secrets are missing. Please call use_secrets to register the missing secrets.\n'
                    'Missing secrets:\n{}'.format('\n'.join(missing_secret_ids))
                )
                self.missing_secret_ids = missing_secret_ids

        raise MissingSecretsError(missing_secrets)

    # Steps are immutable so we don't need to create a full deepcopy of them when cloning Dataflows.
    def __deepcopy__(self, memodict=None):
        return copy(self)

    def __getitem__(self, key):
        if isinstance(key, slice) or isinstance(key, int):
            return Dataflow(self._engine_api, self._steps[key])
        elif isinstance(key, str):
            return col(key)
        elif isinstance(key, Iterable):
            return col(list(key))
        else:
            raise TypeError("Invalid argument type.")

    # Will fold the right Dataflow into the left by appending the rights steps to the lefts.
    def __add__(self, other):
        if not isinstance(other, Dataflow):
            raise TypeError("Can only add two Dataflow objects together. Was given: " + str(type(other)))
        return Dataflow(self._engine_api, self._steps + other._steps)

    def __repr__(self):
        result = dedent("""\
        Dataflow
          steps: [\n""".format(**vars(self)))
        result += ''.join(
            indent(str(step), '  ' * 2) + ',\n'
            for step in self._steps)
        result += '  ]'
        return result

    @staticmethod
    def join(left_dataflow: DataflowReference,
             right_dataflow: DataflowReference,
             join_key_pairs: List[Tuple[str, str]] = None,
             join_type: JoinType = JoinType.MATCH,
             left_column_prefix: str = 'l_',
             right_column_prefix: str = 'r_',
             left_non_prefixed_columns: List[str] = None,
             right_non_prefixed_columns: List[str] = None) -> 'Dataflow':
        """
        Creates a new Dataflow that is a result of joining two provided Dataflows.

        :param left_dataflow: Left Dataflow or DataflowReference to join with.
        :param right_dataflow: Right Dataflow or DataflowReference to join with.
        :param join_key_pairs: Key column pairs. List of tuples of columns names where each tuple forms a key pair to
            join on. For instance: [('column_from_left_dataflow', 'column_from_right_dataflow')]
        :param join_type: Type of join to perform. Match is default.
        :param left_column_prefix: Prefix to use in result Dataflow for columns originating from left_dataflow.
            Needed to avoid column name conflicts at runtime.
        :param right_column_prefix: Prefix to use in result Dataflow for columns originating from right_dataflow.
            Needed to avoid column name conflicts at runtime.
        :param left_non_prefixed_columns: List of column names from left_dataflow that should not be prefixed with
            left_column_prefix. Every other column appearing in the data at runtime will be prefixed.
        :param right_non_prefixed_columns: List of column names from right_dataflow that should not be prefixed with
            left_column_prefix. Every other column appearing in the data at runtime will be prefixed.
        :return: The new Dataflow.
        """

        df = Dataflow(get_engine_api())
        return df.add_step('TwoWayJoin', {
            'leftActivityReference': left_dataflow if isinstance(left_dataflow, ActivityReference)
            else make_activity_reference(left_dataflow),
            'rightActivityReference': right_dataflow if isinstance(right_dataflow, ActivityReference)
            else make_activity_reference(right_dataflow),
            'joinKeyPairs': [{'leftKeyColumn': pair[0], 'rightKeyColumn': pair[1]} for pair in join_key_pairs],
            'joinType': join_type,
            'leftColumnPrefix': left_column_prefix,
            'rightColumnPrefix': right_column_prefix,
            'leftNonPrefixedColumns': left_non_prefixed_columns,
            'rightNonPrefixedColumns': right_non_prefixed_columns
        })

    def keep_columns(self,
                     columns: MultiColumnSelection,
                     validate_column_exists: bool = False) -> 'Dataflow':
        """
        Keeps the specified columns and drops all others.

        :param columns: The source columns.
        :param validate_column_exists: Whether to validate the columns selected.
        :return: The modified Dataflow.
        """
        df = self.add_step('Microsoft.DPrep.KeepColumnsBlock', {
                               'columns': column_selection_to_selector_value(columns)
                           })

        if validate_column_exists:
            df.verify_has_data()

        return df

# >>> BEGIN GENERATED METHODS
    @staticmethod
    def reference(reference: 'DataflowReference') -> 'Dataflow':
        """
        Creates a reference to an existing activity object.

        :param reference: The reference activity.
        :return: A new Dataflow.
        """
        df = Dataflow(get_engine_api())
        return df.add_step('Microsoft.DPrep.ReferenceBlock', {
                               'reference': make_activity_reference(reference)
                           })

    @staticmethod
    def read_parquet_dataset(path: FileDataSource) -> 'Dataflow':
        """
        Creates a step to read parquet file.

        :param path: The path to the Parquet file.
        :return: A new Dataflow.
        """
        df = Dataflow(get_engine_api())
        return df.add_step('Microsoft.DPrep.ReadParquetDatasetBlock', {
                               'path': path.underlying_value
                           })

    def map_column(self,
                   column: str,
                   new_column_id: str,
                   replacements: Optional[List[ReplacementsValue]] = None) -> 'Dataflow':
        """
        Creates a new column where matching values in the source column have been replaced with the specified values.

        :param column: The source column.
        :param new_column_id: The name of the mapped column.
        :param replacements: The values to replace and their replacements.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.MapColumnBlock', {
                                 'column': single_column_to_selector_value(column),
                                 'newColumnId': new_column_id,
                                 'replacements': [p._to_pod() for p in replacements] if replacements is not None else None
                             })

    def null_coalesce(self,
                      columns: List[str],
                      new_column_id: str) -> 'Dataflow':
        """
        For each record, selects the first non-null value from the columns specified and uses it as the value of a new column.

        :param columns: The source columns.
        :param new_column_id: The name of the new column.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.NullCoalesceBlock', {
                                 'columns': [single_column_to_selector_value(p) for p in columns],
                                 'newColumnId': new_column_id
                             })

    def extract_error_details(self,
                              column: str,
                              error_value_column: str,
                              extract_error_code: bool = False,
                              error_code_column: Optional[str] = None) -> 'Dataflow':
        """
        Extracts the error details from error values into a new column.

        :param column: The source column.
        :param error_value_column: Name of a column to hold the original value of the error.
        :param extract_error_code: Whether to also extract the error code.
        :param error_code_column: Name of a column to hold the error code.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ExtractErrorDetailsBlock', {
                                 'column': single_column_to_selector_value(column),
                                 'errorValueColumn': error_value_column,
                                 'extractErrorCode': extract_error_code,
                                 'errorCodeColumn': error_code_column
                             })

    def duplicate_column(self,
                         column_pairs: Dict[str, str]) -> 'Dataflow':
        """
        Creates new columns that are duplicates of the specified source columns.

        :param column_pairs: Mapping of the columns to duplicate to their new names.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.DuplicateColumnBlock', {
                                 'columnPairs': [{'column': single_column_to_selector_value(k), 'newColumnId': v} for k, v in column_pairs.items()]
                             })

    def split_stype(self,
                    column: str,
                    stype: SType,
                    stype_fields: Optional[List[str]] = None,
                    new_column_names: Optional[List[str]] = None) -> 'Dataflow':
        """
        Creates new columns from an existing column, interpreting its values as a semantic type.

        :param column: The source column.
        :param stype: The semantic type used to interpret values in the column.
        :param stype_fields: Fields of the semantic type to use. If not provided, all fields will be used.
        :param new_column_names: Names of the new columns. If not provided new columns will be named with the source column name plus the semantic type field name.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.SplitSTypeBlock', {
                                 'column': single_column_to_selector_value(column),
                                 'stype': stype.value,
                                 'stypeFields': [p for p in stype_fields] if stype_fields is not None else None,
                                 'newColumnNames': [p for p in new_column_names] if new_column_names is not None else None
                             })

    def replace_na(self,
                   columns: MultiColumnSelection,
                   use_default_na_list: bool = True,
                   use_empty_string_as_na: bool = True,
                   use_nan_as_na: bool = True,
                   custom_na_list: Optional[str] = None) -> 'Dataflow':
        """
        Replaces values in the specified columns with nulls. You can choose to use the default list, supply your own, or both.

        :param use_default_na_list: Use the default list and replace 'null', 'NaN', 'NA', and 'N/A' with null.
        :param use_empty_string_as_na: Replace empty strings with null.
        :param use_nan_as_na: Replace NaNs with Null.
        :param custom_na_list: Provide a comma separated list of values to replace with null.
        :param columns: The source columns.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ReplaceNaBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'useDefaultNaList': use_default_na_list,
                                 'useEmptyStringAsNa': use_empty_string_as_na,
                                 'useNanAsNa': use_nan_as_na,
                                 'customNaList': custom_na_list
                             })

    def trim_string(self,
                    columns: MultiColumnSelection,
                    trim_left: bool = True,
                    trim_right: bool = True,
                    trim_type: TrimType = TrimType.WHITESPACE,
                    custom_characters: str = '') -> 'Dataflow':
        """
        Trims string values in specific columns.

        :param columns: The source columns.
        :param trim_left: Whether to trim from the beginning.
        :param trim_right: Whether to trim from the end.
        :param trim_type: Whether to trim whitespace or custom characters.
        :param custom_characters: The characters to trim.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.TrimStringBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'trimLeft': trim_left,
                                 'trimRight': trim_right,
                                 'trimType': trim_type.value,
                                 'customCharacters': custom_characters
                             })

    def round(self,
              column: str,
              decimal_places: int) -> 'Dataflow':
        """
        Rounds the values in the column specified to the desired number of decimal places.

        :param column: The source column.
        :param decimal_places: The number of decimal places.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.RoundBlock', {
                                 'column': single_column_to_selector_value(column),
                                 'decimalPlaces': decimal_places
                             })

    def clip(self,
             columns: MultiColumnSelection,
             lower: Optional[float] = None,
             upper: Optional[float] = None,
             use_values: bool = True) -> 'Dataflow':
        """
        Clips values so that all values are between the lower and upper boundaries.

        :param columns: The source columns.
        :param lower: All values lower than this value will be set to this value.
        :param upper: All values higher than this value will be set to this value.
        :param use_values: If true, values outside boundaries will be set to the boundary values. If false, those values will be set to null.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ClipBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'lower': lower,
                                 'upper': upper,
                                 'useValues': use_values
                             })

    def str_replace(self,
                    columns: MultiColumnSelection,
                    value_to_find: Optional[str] = None,
                    replace_with: Optional[str] = None,
                    match_entire_cell_contents: bool = False,
                    use_special_characters: bool = False) -> 'Dataflow':
        """
        Replaces values in a string column that match a search string with the specified value.

        :param columns: The source columns.
        :param value_to_find: The value to find.
        :param replace_with: The replacement value.
        :param match_entire_cell_contents: Whether the value to find must match the entire value.
        :param use_special_characters: If checked, you can use '#(tab)', '#(cr)', or '#(lf)' to represent special characters in the find or replace arguments.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.StrReplaceBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'valueToFind': value_to_find,
                                 'replaceWith': replace_with,
                                 'matchEntireCellContents': match_entire_cell_contents,
                                 'useSpecialCharacters': use_special_characters
                             })

    def distinct_rows(self) -> 'Dataflow':
        """
        Filters out records that contain duplicate values in all columns, leaving only a single instance.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.DistinctRowsBlock', {
                             })

    def drop_nulls(self,
                   columns: MultiColumnSelection,
                   column_relationship: typedefinitions.ColumnRelationship = typedefinitions.ColumnRelationship.ALL) -> 'Dataflow':
        """
        Drops rows where all or any of the selected columns are null.

        :param columns: The source columns.
        :param column_relationship: Whether all or any of the selected columns must be null.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.DropNullsBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'columnRelationship': column_relationship.value
                             })

    def drop_errors(self,
                    columns: MultiColumnSelection,
                    column_relationship: typedefinitions.ColumnRelationship = typedefinitions.ColumnRelationship.ALL) -> 'Dataflow':
        """
        Drops rows where all or any of the selected columns are an Error.

        :param columns: The source columns.
        :param column_relationship: Whether all or any of the selected columns must be an Error.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.DropErrorsBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'columnRelationship': column_relationship.value
                             })

    def distinct(self,
                 columns: MultiColumnSelection) -> 'Dataflow':
        """
        Filters out records that contain duplicate values in the specified columns, leaving only a single instance.

        :param columns: The source columns.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.DistinctBlock', {
                                 'columns': column_selection_to_selector_value(columns)
                             })

    def skip(self,
             count: int) -> 'Dataflow':
        """
        Skips the specified number of records.

        :param count: The number of records to skip.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.SkipBlock', {
                                 'count': count
                             })

    def take(self,
             count: int) -> 'Dataflow':
        """
        Takes the specified count of records.

        :param count: The number of records to take.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.TakeBlock', {
                                 'count': count
                             })

    def rename_columns(self,
                       column_pairs: Dict[str, str]) -> 'Dataflow':
        """
        Renames the specified columns.

        :param column_pairs: The columns to rename and the desired new names.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.RenameColumnsBlock', {
                                 'columnPairs': [{'column': single_column_to_selector_value(k), 'newColumnId': v} for k, v in column_pairs.items()]
                             })

    def drop_columns(self,
                     columns: MultiColumnSelection) -> 'Dataflow':
        """
        Drops the specified columns.

        :param columns: The source columns.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.DropColumnsBlock', {
                                 'columns': column_selection_to_selector_value(columns)
                             })

    def promote_headers(self) -> 'Dataflow':
        """
        Sets the first record in the dataset as headers, replacing any existing ones.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.PromoteHeadersBlock', {
                             })

    def to_number(self,
                  columns: MultiColumnSelection,
                  decimal_point: DecimalMark = DecimalMark.DOT) -> 'Dataflow':
        """
        Converts the values in the specified columns to floating point numbers.

        :param columns: The source columns.
        :param decimal_point: The symbol to use as the decimal mark.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ToNumberBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'decimalPoint': decimal_point.value
                             })

    def to_bool(self,
                columns: MultiColumnSelection,
                true_values: List[str],
                false_values: List[str],
                mismatch_as: MismatchAsOption = MismatchAsOption.ASERROR) -> 'Dataflow':
        """
        Converts the values in the specified columns to booleans.

        :param columns: The source columns.
        :param true_values: The values to treat as true.
        :param false_values: The values to treat as false.
        :param mismatch_as: How to treat values that don't match the values in the true or false values lists.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ToBoolBlock', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'trueValues': [p for p in true_values],
                                 'falseValues': [p for p in false_values],
                                 'mismatchAs': mismatch_as.value
                             })

    def to_string(self,
                  columns: MultiColumnSelection) -> 'Dataflow':
        """
        Converts the values in the specified columns to strings.

        :param columns: The source columns.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ToStringBlock', {
                                 'columns': column_selection_to_selector_value(columns)
                             })

    def to_long(self,
                columns: MultiColumnSelection) -> 'Dataflow':
        """
        Converts the values in the specified columns to 64 bit integers.

        :param columns: The source columns.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ToLongBlock', {
                                 'columns': column_selection_to_selector_value(columns)
                             })

    def convert_unix_timestamp_to_datetime(self,
                                           columns: MultiColumnSelection,
                                           use_seconds: bool = False) -> 'Dataflow':
        """
        Converts the specified column to DateTime values by treating the existing value as a Unix timestamp.

        :param columns: The source columns.
        :param use_seconds: Whether to use seconds as the resolution. Milliseconds are used if false.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.ConvertUnixTimestampToDateTime', {
                                 'columns': column_selection_to_selector_value(columns),
                                 'useSeconds': use_seconds
                             })

    def _summarize(self,
                   summary_columns: Optional[List[SummaryColumnsValue]] = None,
                   group_by_columns: Optional[List[str]] = None,
                   join_back: bool = False,
                   join_back_columns_prefix: Optional[str] = None) -> 'Dataflow':
        """
        Summarizes data by running aggregate functions over specific columns. The aggregate functions are independent and it is possible to aggregate
            the same column multiple times. Unique names have to be provided for the resulting columns. The aggregations can be grouped, in which
            case one record is returned per group; or ungrouped, in which case one record is returned for the whole dataset. Additionally, the
            results of the aggregations can either replace the current dataset or augment it by appending the result columns.

        :param summary_columns: Column summarization definition.
        :param group_by_columns: Columns to group by.
        :param join_back: Whether to append subtotals or replace current data with them.
        :param join_back_columns_prefix: Prefix to use for subtotal columns when appending them to current data.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.SummarizeBlock', {
                                 'summaryColumns': [p._to_pod() for p in summary_columns] if summary_columns is not None else None,
                                 'groupByColumns': [p for p in group_by_columns] if group_by_columns is not None else None,
                                 'joinBack': join_back,
                                 'joinBackColumnsPrefix': join_back_columns_prefix
                             })

    def append_columns(self,
                       dataflows: List['DataflowReference']) -> 'Dataflow':
        """
        Appends the columns from the referenced dataflows to the current one. Duplicate columns will result in failure.

        :param dataflows: The dataflows to append.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.AppendColumnsBlock', {
                                 'dataflows': [make_activity_reference(p) for p in dataflows]
                             })

    def append_rows(self,
                    dataflows: List['DataflowReference']) -> 'Dataflow':
        """
        Appends the records in the specified dataflows to the current one. If the schemas of the dataflows are distinct, this will result in records
            with different schemas.

        :param dataflows: The dataflows to append.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.AppendRowsBlock', {
                                 'dataflows': [make_activity_reference(p) for p in dataflows]
                             })

    def sort(self,
             sort_order: List[Tuple[str, bool]]) -> 'Dataflow':
        """
        Sorts the dataset by the specified columns.

        :param sort_order: The columns to sort by and whether to sort ascending or descending. True is treated as descending, false as ascending.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.SortBlock', {
                                 'sortOrder': [{'column': single_column_to_selector_value(t[0]), 'descending': t[1]} for t in sort_order]
                             })

    def write_streams(self,
                      streams_column: str,
                      base_path: FileOutput,
                      file_names_column: Optional[str] = None) -> 'Dataflow':
        """
        Writes the streams in the specified column to the destination path. By default, the name of the files written will be the resource identifier
            of the streams. This behavior can be overriden by specifying a column which contains the names to use.

        :param streams_column: The column containing the streams to write.
        :param file_names_column: A column containing the file names to use.
        :param base_path: The path under which the files should be written.
        :return: The modified Dataflow.
        """
        return self.add_step('Microsoft.DPrep.WriteStreamsBlock', {
                                 'streamsColumn': single_column_to_selector_value(streams_column),
                                 'basePath': base_path.underlying_value,
                                 'fileNamesColumn': single_column_to_selector_value(file_names_column) if file_names_column is not None else None
                             })

    def parse_json_column(self,
                          column: str) -> 'Dataflow':
        """
        Parses the values in the specified column as JSON objects and expands them into multiple columns.

        :param column: The source column.
        :return: The modified Dataflow.
        """
        args = {
            'column': single_column_to_selector_value(column)
        }
        blocks = steps_to_block_datas(self._get_steps())
        new_block = self._engine_api.add_block_to_list(
            AddBlockToListMessageArguments(blocks = blocks,
                                           new_block_arguments=BlockArguments(PropertyValues.from_pod(args), 'Microsoft.DPrep.ParseJsonColumnBlock')))
        return self.add_step('Microsoft.DPrep.ParseJsonColumnBlock', new_block.arguments.to_pod(), new_block.local_data.to_pod())
# <<< END GENERATED METHODS
