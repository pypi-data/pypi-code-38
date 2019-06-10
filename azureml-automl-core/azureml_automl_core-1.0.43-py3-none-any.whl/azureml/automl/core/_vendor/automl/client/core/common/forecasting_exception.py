# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A module that contains definitions of custom exception classes."""


# TODO Rename this
class AzureMLForecastException(Exception):
    """Base exception class for all exceptions in the Azure ML Forecasting toolkit."""

    pass


class PipelineException(AzureMLForecastException):
    """
    Exception raised for errors in AzureMLForecastPipeline.

    Attributes:
        message: terse error message as defined in 'Messages' class of the
            'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, message, error_detail=None):
        """Create a PipelineException."""
        if error_detail is not None:
            super().__init__("PipelineException: {0}, {1}".format(message, error_detail))
        else:
            super().__init__("PipelineException: {0}".format(message))


class TransformException(AzureMLForecastException):
    """
    Exception raised for errors in a transform class in the AzureML Forecasting SDK.

    Attributes:
        message: terse error message as defined in 'Messages' class of the 'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, message, error_detail=None):
        """Create a TransformException."""
        if error_detail is not None:
            super().__init__("TransformException: {0}, {1}".format(message, error_detail))
        else:
            super().__init__("TransformException: {0}".format(message))


class TransformValueException(TransformException):
    """
    Exception raised for value errors in a transform class in the AzureML Forecasting SDK.

    :param message:
        terse error message as defined in 'Messages'
        class of the 'verify' module
    :type message: str

    :param error_detail: optional, detailed error message
    :type error_detail: str
    """

    def __init__(self, message, error_detail=None):
        """Create a TransformValueException."""
        if error_detail is not None:
            super().__init__("TransformValueException: {0}, {1}"
                             .format(message, error_detail))
        else:
            super().__init__("TransformValueException: {0}".format(message))


class TransformTypeException(TransformException):
    """
    Exception raised for type errors in a transform class in the AzureML Forecasting SDK.

    :param message:
        terse error message as defined in 'Messages'
        class of the 'verify' module
    :type message: str

    :param error_detail: optional, detailed error message
    :type error_detail: str
    """

    def __init__(self, message, error_detail=None):
        """Create a TransformTypeException."""
        if error_detail is not None:
            super().__init__("TransformTypeException: {0}, {1}"
                             .format(message, error_detail))
        else:
            super().__init__("TransformTypeException: {0}".format(message))


class NotTimeSeriesDataFrameException(AzureMLForecastException):
    """
    Exception raised if the data frame is not of TimeSeriesDataFrame.

    Attributes:
        message: terse error message as defined in 'Messages' class of the 'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, message, error_detail=None):
        """Create a NotTimeSeriesDataFrameException."""
        if error_detail is not None:
            super().__init__("NotTimeSeriesDataFrameException: {0}, {1}".format(message, error_detail))
        else:
            super().__init__("NotTimeSeriesDataFrameException: {0}".format(message))


class InvalidEstimatorTypeException(AzureMLForecastException):
    """InvalidEstimatorTypeException."""

    def __init__(self, message, error_detail=None):
        """Create an InvalidEstimatorTypeException."""
        if error_detail is not None:
            super().__init__("InvalidEstimatorTypeException: {0}, {1}".format(message, error_detail))
        else:
            super().__init__("InvalidEstimatorTypeException: {0}".format(message))


class NotSupportedException(AzureMLForecastException):
    """NotSupportedException."""

    def __init__(self, message, error_detail=None):
        """Create a NotSupportedException."""
        if error_detail is not None:
            super().__init__("NotSupportedException: {0}, {1}".format(message, error_detail))
        else:
            super().__init__("NotSupportedException: {0}".format(message))


class EstimatorTypeException(AzureMLForecastException):
    """EstimatorTypeException."""

    def __init__(self, message):
        """Create an EstimatorTypeException."""
        super().__init__("Estimator type is invalid. {0}".format(message))


class EstimatorValueException(AzureMLForecastException):
    """EstimatorValueException."""

    def __init__(self, message):
        """Create an EstimatorValueException."""
        super().__init__("Estimator value is invalid. {0}".format(message))


class DataFrameTypeException(AzureMLForecastException):
    """DataFrameTypeException."""

    def __init__(self, message):
        """Create a DataFrameTypeException."""
        super().__init__("Data frame type is invalid. {0}".format(message))


class DataFrameValueException(AzureMLForecastException):
    """DataFrameValueException."""

    def __init__(self, message):
        """Create a DataFrameValueException."""
        super().__init__("Data frame value is invalid. {0}".format(message))


class DataFrameMissingColumnException(AzureMLForecastException):
    """DataFrameMissingColumnException."""

    def __init__(self, message):
        """Create a DataFrameMissingColumnException."""
        super().__init__("Data frame is missing a required column. {0}".format(message))


class DatetimeConversionException(AzureMLForecastException):
    """DatetimeConversionException."""

    def __init__(self, message):
        """Create a DateTimeConversionException."""
        super().__init__("Unable to do datetime conversion. {0}".format(message))


class DataFrameIncorrectFormatException(AzureMLForecastException):
    """DataFrameIncorrectFormatException."""

    def __init__(self, message, error_detail=None):
        """Create a DataFrameIncorrectFormatException."""
        if error_detail is not None:
            super().__init__("DataFrameIncorrectFormatException: {0}, {1}".format(message, error_detail))
        else:
            super().__init__("DataFrameIncorrectFormatException: {0}".format(message))


class DataFrameProcessingException(AzureMLForecastException):
    """DataFrameProcessingException."""

    def __init__(self, message):
        """Create a DataFrameProcessingException."""
        super().__init__("Exception occurred when processing a time series dataframe. {0}".format(message))


class MultiSeriesFitNotSupportedException(AzureMLForecastException):
    """A generic exception raised when a learner does not supported multi-series fit."""

    def __init__(self, message):
        """Create a MultiSeriesFitNotSupportedException."""
        super().__init__("MultiSeriesFitNotSupportedException: {0}".format(message))


class JobTypeNotSupportedException(AzureMLForecastException):
    """Exception thrown by a compute backend for an unsupported job type."""

    def __init__(self, message):
        """Create a JobTypeNotSupportedException."""
        super().__init__("JobTypeNotSupportedException: {0}".format(message))


class SchedulerException(AzureMLForecastException):
    """Exception thrown by a ftk.compute.scheduler.Scheduler object."""

    def __init__(self, message):
        """Create a SchedulerException."""
        super().__init__("SchedulerException: {0}".format(message))
