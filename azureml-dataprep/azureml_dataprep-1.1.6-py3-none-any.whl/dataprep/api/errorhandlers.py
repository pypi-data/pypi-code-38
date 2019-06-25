# Copyright (c) Microsoft Corporation. All rights reserved.
# pylint: disable=line-too-long
error_messages = {
    'AccessDenied': 'You do not have permission to the specified path or file.',
    'AllLinesAreSkipped': 'All data rows are skipped.',
    'AssertionFailed': 'Assertion failed.',
    'BoolValuesConflict': 'Could not convert the same value to both True and False.',
    'CacheFolderPathMissing': 'No cache folder provided. Please provide a cache folder path in App Settings or in the Cache step.',
    'CachingAborted': 'Caching has been aborted.',
    'ColumnInCustomBlockMissing': 'A column that does not exist was referenced in a custom code block.',
    'DatabaseConnectionError': 'Could not connect to specified database.',
    'DatabaseLoginError': 'Login failed.',
    'DatabaseLoginOrConnectionError': 'Either login failed or could not connect to specified database.',
    'DatabaseServerConnectionError': 'The server was not found or was not accessible.',
    'DateTimeFormatParseFailed': None,
    'DriverNotFoundError': 'Driver or Class Not Found for the executed operation. If it is sql query please verify the correct version of the specific database driver is present.',
    'DuplicateColumnName': 'Join will produce duplicate column names. Set the column name prefix.',
    'EmptySteps': 'No steps found in the dataflow. Please make sure there are steps in the dataflow.',
    'ErrorInDependency': 'There is error in dependency Dataflow.',
    'ExpressionError': 'The provided expression failed with error: ',
    'FailedToCacheData': 'Failed to generate a cache from the previous steps.',
    'FailedToDownloadSampleCache': 'Failed to download the remote sample cache to your local machine. Please ensure your local machine has access to the intermediate path or that you\'ve provided an appropriate SAS.',
    'FailedToExpandJson': 'The specified column could not be expanded. Check that column values are valid JSON.',
    'FailedToReadCache': 'Cannot retrieve cache. Please refresh the cache to generate it again.',
    'FailedToSubmitSampleCacheRun': 'Submitting the sample job to your remote runner failed. Please verify the connection details and try again.',
    'FailedToWriteCache': 'Cannot write cache. Please check if the specified cache folder exists.',
    'FieldConflictError': 'Duplicate field found for combined schema. Please ensure column names are unique.',
    'FileOrDirectoryAlreadyExist': 'A file or directory with the same name already exists.',
    'IOExceptionOnCreate': 'An I/O error occurred while creating the file with the specified path.',
    'InvalidColumnName': 'The specified column name is not valid.',
    'InvalidPath': 'The provided path is not valid or the files could not be accessed.',
    'InvalidSchema': 'The schema returned by the operation is not valid. Please ensure the resulting data frame contains only columns with no levels.',
    'JSONReadError': 'Sorry, we were not able to open the requested JSON file. It is in a format that we could not understand. Please send us feedback about this file’s JSON structure.',
    'MismatchedHeaders': 'Column headers don\'t match between selected files',
    'MissingLeftKey': 'Join key column does not exist in the left source Dataflow.',
    'MissingLeftSource': 'The left source Dataflow does not exist.',
    'MissingRightKey': 'Join key column does not exist in the right source Dataflow.',
    'MissingRightSource': 'The right source Dataflow does not exist.',
    'NoLabelsFound': 'Failed to find categorical labels. Please specify labels manually or use a column with less than 1000 unique values.',
    'NothingToTrim': 'Trim String failed because nothing was chosen to trim.',
    'OperatorRequiresValue': 'An operator in this filter is missing a value.',
    'PathTooLong': 'The specified path, file name, or both exceed the system-defined maximum length.',
    'PythonPathInvalid': 'Cannot start a Python process with the path provided. Please provide a different Python path.',
    'QueryExecutionError': 'Could not execute provided query.',
    'ReadFormatError': 'This data source cannot be parsed with the selected format.',
    'ReplaceMissingRequiresSelector': 'You must choose at least one of the options to identify missing values.',
    'ReplaceNaValuesFailedNothingToReplace': 'Please provide the set of values that should be replaced.',
    'ReplaceRequiresValue': 'The Replace With field is missing a value, or choose to Replace With Nothing.',
    'ReplaceValuesFailedNothingToReplace': 'Please provide a value to find.',
    'ResourceCredentialsMissing': 'The required credentials to access this resource are missing. Please edit the block to re-enter them.',
    'SampleCacherMissing': 'The runner selected for this sample is missing from your system. Please select a different runner.',
    'SampleDisabled': 'The specified sample is disabled because it is not compatible with your data source. Please edit it and try again.',
    'SampleMissing': 'The specified sample is missing. Please refresh the sample to generate it again.',
    'SplitColumnProgramGenerationFailed': 'We were not able to split this column.',
    'StorageError': 'Storage Error: ',
    'TargetColumnMissing': 'The target column is not present in the current data set.',
    'TrimStringCustomCannotBeEmpty': 'The Custom Trim Characters value cannot be empty or only whitespace.',
    'TrimStringRequiresLeadingOrTrailing': 'You must choose at least one option from Trim Leading and Trim Trailing.',
    'UnauthorizedAccess': 'Could not access the specified path due to permission or read-only properties.',
    'Uncategorized': 'Could not execute the specified transform.',
    'UnknownDateFormat': 'The format of the date value specified was not in the correct format, YYYY-MM-DD.',
    'UnknownExpressionError': 'The provided expression failed to be evaluated.',
    'UnsupportedColumnType': 'Table contains unsupported column type (Variant).',
    'UnsupportedParquetFile': 'Unsupported Parquet file. Try reading with \'read_parquet_dataset\'.',
    'WrongEncoding': 'The file could not be read using the specified encoding.',
    'WrongEncodingWrite': 'The file could not be written using the specified encoding.'
}


def raise_engine_error(error_response):
    error_code = error_response['errorCode']
    if 'DatabaseConnectionError' in error_code:
        raise ExecutionError(error_response)
    if 'DatabaseServerConnectionError' in error_code:
        raise ExecutionError(error_response)
    if 'DatabaseLoginError' in error_code:
        raise ExecutionError(error_response)
    if 'DatabaseLoginOrConnectionError' in error_code:
        raise ExecutionError(error_response)
    if 'DriverNotFound' in error_code:
        raise ExecutionError(error_response)
    if 'ActivityExecutionFailed' in error_code:
        raise ExecutionError(error_response)
    elif 'UnableToPreviewDataSource' in error_code:
        raise ExecutionError(error_response)
    elif 'EmptySteps' in error_code:
        raise EmptyStepsError()
    else:
        raise UnexpectedError(error_response)


class ExecutionError(Exception):
    """
    Exception raised when dataflow execution fails.
    """
    def __init__(self, error_response):
        error_code = error_response['errorData']['errorCode'] if 'errorCode' in error_response['errorData'] else None
        error_message = error_response['errorData']['errorMessage'] if 'errorMessage' in error_response['errorData'] \
            else error_response['message'] if 'message' in error_response \
            else ''
        message = error_messages[error_code] if error_code is not None else ''
        if ((error_code == 'ExpressionError' or error_code == 'StorageError' or error_code is None)
                and error_message is not None):
            message += error_message
        super().__init__(message if message is not None else error_message)


class EmptyStepsError(Exception):
    """
    Exception raised when there are issues with steps in the dataflow.
    """
    def __init__(self):
        super().__init__('The Dataflow contains no steps and cannot be executed. '
                         'Use a reader to create a Dataflow that can load data.')


class UnexpectedError(Exception):
    """
    Unexpected error.

    :var error: Error code of the failure.
    """
    def __init__(self, error):
        self.error = error


class PandasImportError(Exception):
    """
    Exception raised when pandas was not able to be imported.
    """
    _message = 'Could not import pandas. Ensure a compatible version is installed by running: pip install azureml-dataprep[pandas]'
    def __init__(self):
        print('PandasImportError: ' + self._message)
        super().__init__(self._message)


class NumpyImportError(Exception):
    """
    Exception raised when numpy was not able to be imported.
    """
    _message = 'Could not import numpy. Ensure a compatible version is installed by running: pip install azureml-dataprep[pandas]'
    def __init__(self):
        print('NumpyImportError: ' + self._message)
        super().__init__(self._message)
