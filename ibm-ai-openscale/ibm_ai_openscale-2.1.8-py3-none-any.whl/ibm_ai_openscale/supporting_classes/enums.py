# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class MetricTypes:
    """
    Describes possible metrics types for listing deployment_metrics.

    Contains: [QUALITY_MONITORING, PERFORMANCE_MONITORING, FAIRNESS_MONITORING, CUSTOM_MONITORING]
    """
    QUALITY_MONITORING = 'quality'
    PERFORMANCE_MONITORING = 'performance'
    FAIRNESS_MONITORING = 'fairness'
    CUSTOM_MONITORING = 'custom'


class MetricsFormat:
    """
    Describes possible metrics formats.

    Contains: [SAMPLES, TIME_SERIES]
    """
    SAMPLES = 'samples'
    TIME_SERIES = 'time_series'


class Choose:
    """
    Describes possible options of choosing result from table filtering when only one result is required.

    Contains: [FIRST, LAST, RANDOM]
    """
    FIRST = 'first'
    LAST = 'last'
    RANDOM = 'random'


class InputDataType:
    """
    Describes possible model input data types.

    Contains: [STRUCTURED, UNSTRUCTURED_IMAGE, UNSTRUCTURED_TEXT, UNSTRUCTURED_AUDIO, UNSTRUCTURED_VIDEO]
    """
    STRUCTURED = 'structured'
    UNSTRUCTURED_IMAGE = 'unstructured_image'
    UNSTRUCTURED_TEXT = 'unstructured_text'
    UNSTRUCTURED_AUDIO = 'unstructured_audio'
    UNSTRUCTURED_VIDEO = 'unstructured_video'


class ProblemType:
    """
    Describes possible model (problem) types.

    Contains: [REGRESSION, BINARY_CLASSIFICATION, MULTICLASS_CLASSIFICATION]
    """
    REGRESSION = 'regression'
    BINARY_CLASSIFICATION = 'binary'
    MULTICLASS_CLASSIFICATION = 'multiclass'


class FeedbackFormat:
    """
    Describes supported types of feedback format.

    Contains: [WML, DICT, CSV]
    """
    WML = 'wml'
    DICT = 'dict'
    CSV = 'text'
