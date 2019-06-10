"""
Main Data Prep module that contains tools to load, analyze and manipulate data.
To learn more about the advantages, key functionalities and supported platforms of Data Prep, you may refer to https://aka.ms/data-prep-sdk.
"""
# Copyright (c) Microsoft Corporation. All rights reserved.
# Here many parts of the DataPrep API are re-exported under the 'azureml.dataprep' namespace for convenience.

# extend_path searches all directories on sys.path for any packages that exists under the same namespace
# as __name__. This handles different modules from the same namespace being installed in different places.
# https://docs.python.org/3.6/library/pkgutil.html#pkgutil.extend_path

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

# Builders
from .api.builders import InferenceArguments, FileFormatArguments, SourceData, ImputeColumnArguments
from .api.engineapi.typedefinitions import ReplaceValueFunction, StringMissingReplacementOption

# Dataflow
from .api.dataflow import Dataflow, DataflowReference, ReplacementsValue, HistogramArgumentsValue, \
    KernelDensityArgumentsValue, SummaryColumnsValue, SummaryFunction, JoinType, SType

# Engine Types used by Dataflow
from .api.engineapi.typedefinitions import ColumnRelationship, DecimalMark, TrimType, \
    MismatchAsOption, AssertPolicy

# DataProfile
from .api.dataprofile import ColumnProfile, DataProfile, HistogramBucket, ValueCountEntry, TypeCountEntry, STypeCountEntry

# DataSources
from .api.datasources import Path, LocalDataSource, BlobDataSource, DatabaseAuthType, MSSQLDataSource, PostgreSQLDataSource, \
    LocalFileOutput, BlobFileOutput

# Expressions
from .api.expressions import col, f_not, f_and, f_or, cond, Expression, ExpressionLike, value

# Functions
from .api.functions import round, trim_string, get_stream_name, RegEx, create_datetime

# Parse Properties
from .api.parseproperties import ParseDelimitedProperties, ParseFixedWidthProperties, ParseLinesProperties, \
    ParseParquetProperties, ReadExcelProperties, ReadJsonProperties, ParseDatasourceProperties

# Readers
from .api.readers import FilePath, read_csv, read_fwf, read_excel, read_lines, read_sql, read_postgresql, read_parquet_file, \
    read_parquet_dataset, read_json, detect_file_format, smart_read_file, auto_read_file, read_pandas_dataframe, SkipMode, \
    PromoteHeadersMode, FileEncoding
from .api._archiveoption import ArchiveOptions
from .api.engineapi.typedefinitions import ArchiveType

# References
from .api.references import ExternalReference

# Secret Manager
from .api.secretmanager import Secret, register_secrets, register_secret, create_secret

# Steps
from .api.step import ColumnSelector, MultiColumnSelection, Step

# Type Conversions
from .api.typeconversions import FieldType, TypeConverter, DateTimeConverter, CandidateDateTimeConverter, \
    CandidateConverter, InferenceInfo

# Types
from .api.types import SplitExample, Delimiters

# AML
from .api._datastore_helper import login

# Error handling
from .api.errorhandlers import ExecutionError, UnexpectedError

# Spark execution
from .api.sparkexecution import DataPrepImportError, set_execution_mode

# Profile Diff related objects
from .api.engineapi.typedefinitions import (HistogramCompareMethod, ColumnProfileDifference, DataProfileDifference)

# Expose types for documentation
__all__ = ['Dataflow', 'read_csv', 'read_fwf', 'read_excel', 'read_lines', 'read_sql', 'read_postgresql', 'read_parquet_file',
           'read_parquet_dataset', 'read_json', 'detect_file_format', 'auto_read_file', 'read_pandas_dataframe',
           'InferenceArguments', 'FilePath', 'SkipMode', 'PromoteHeadersMode', 'FileEncoding', 'JoinType',
           'FileFormatArguments', 'DataflowReference', 'SourceData', 'ImputeColumnArguments', 'ColumnSelector',
           'MultiColumnSelection', 'Path', 'LocalDataSource', 'BlobDataSource', 'DatabaseAuthType', 'MSSQLDataSource', 'PostgreSQLDataSource',
           'LocalFileOutput', 'BlobFileOutput', 'ReplaceValueFunction', 'StringMissingReplacementOption', 'login',
           'ReplacementsValue', 'HistogramArgumentsValue', 'KernelDensityArgumentsValue', 'SummaryColumnsValue',
           'ColumnRelationship', 'DecimalMark', 'SummaryFunction', 'TrimType', 'MismatchAsOption', 'AssertPolicy',
           'TypeConverter', 'FieldType', 'DateTimeConverter', 'CandidateDateTimeConverter', 'CandidateConverter',
           'InferenceInfo', 'ColumnProfile', 'DataProfile', 'HistogramBucket', 'ValueCountEntry', 'TypeCountEntry',
           'ParseDelimitedProperties', 'ParseFixedWidthProperties', 'ParseLinesProperties', 'ParseParquetProperties',
           'ReadExcelProperties', 'ReadJsonProperties', 'ParseDatasourceProperties', 'ExternalReference', 'col', 'f_not', 'f_and', 'f_or',
           'cond', 'Expression', 'ExpressionLike', 'value', 'round', 'trim_string', 'Secret', 'register_secrets',
           'register_secret', 'create_secret', 'SplitExample', 'Delimiters',
           'ExecutionError', 'UnexpectedError', 'DataPrepImportError', 'Step', 'SType', 'STypeCountEntry','HistogramCompareMethod']

__version__ = '1.1.5'
