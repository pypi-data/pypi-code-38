# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definition of constants used by the AML forecasting package."""

LOGGING_PREFIX = 'azureml.timeseries'
LOGGING_DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'
PIPELINE_PREDICT_OPERATION = 'predict'

ORIGIN_TIME_COLNAME_DEFAULT = 'origin'

UNIFORM_PRED_POINT_COLNAME = 'PointForecast'
UNIFORM_PRED_DIST_COLNAME = 'DistributionForecast'
UNIFORM_MODEL_NAME_COLNAME = 'ModelName'
UNIFORM_MODEL_PARAMS_COLNAME = 'ModelParams'

UNIFORM_METADATA_DICT = {
    'pred_point': UNIFORM_PRED_POINT_COLNAME,
    'pred_dist': UNIFORM_PRED_DIST_COLNAME,
    'origin_time_colname': ORIGIN_TIME_COLNAME_DEFAULT,
    'model_colnames': {'model_class': UNIFORM_MODEL_NAME_COLNAME,
                       'param_values': UNIFORM_MODEL_PARAMS_COLNAME}}

FUNC_PARAM_NAME = 'func'
DATA_MAP_FUNC_PARAM_NAME = 'data_map_func'
DATA_PARAM_NAME = 'data'
ARGS_PARAM_NAME = 'args'
KEYWORD_ARGS_PARAM_NAME = 'kwargs'
HORIZON_COLNAME = 'horizon'

#
# Used in time series utility functions
#
SEASONAL_DETECT_FFT_THRESH_SIZE = 1024
SEASONAL_DETECT_MIN_OBS = 5


class Telemetry:
    """Constants used for telemetry."""

    TELEMETRY_COMPONENT = 'component'
    TELEMETRY_FUNCION = 'Function'
    TELEMETRY_MODULE = 'Module'
    TELEMETRY_CLASS = 'Class'
    TELEMETRY_RUN_ID = 'RunID'
    TELEMETRY_NUM_ROWS = 'NumberOfDataRows'
    TELEMETRY_TIME_COLUMN = 'DataTimeColumn'
    TELEMETRY_GRAIN_COLUMNS = 'DataGrainColumns'
    TELEMETRY_ORIGIN_COLUMN = 'DataOriginTimeColumn'
    TELEMETRY_TARGET_COLUMN = 'DataTargetColumn'
    TELEMETRY_GROUP_COLUMNS = 'DataGroupColumns'
    TELEMETRY_DATA_COLUMNS = 'DataColumns'
    TELEMETRY_PIPELINE_ID = 'PipelineID'
    TELEMETRY_PIPELINE_STEPS = 'PipelineSteps'
    TELEMETRY_PIPELINE_STEP_NUM = 'StepNumber'
    TELEMETRY_PIPELINE_SAMPLE_WEIGHT = 'SampleWeight'
