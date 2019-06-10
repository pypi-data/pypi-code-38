# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

DATADRIFT_KEY = "_datadrift"
DATADRIFT_SERVICES = "_services"
DATADRIFT_VERSION = "_version"
DATADRIFT_VERSION_VALUE = 1.0
DATADRIFT_SCHEDULES = "_schedules"
DATADRIFT_SCHEDULE_ID = "_schedule_id"
DATADRIFT_ENABLE = "_enabled"
DATADRIFT_FREQUENCY = "_frequency"
DATADRIFT_DRIFT_THRESHOLD = "_drift_threshold"
DATADRIFT_INTERVAL = "_interval"
DATADRIFT_ALERT_CONFIG = "_alert_config"
DATADRIFT_SCHEDULE_START = "_schedule_start"

METRIC_SCHEMA_VERSION_KEY = "schema_version"
METRIC_SCHEMA_VERSION_DFT = "0.1"
METRIC_SCHEMA_VERSION_CUR = "1.0"

# old key names, keep them for compatibility
METRIC_DATASHIFT_MCC_TEST = "ds_mcc_test"
METRIC_DATASHIFT_MCC_TRAIN = "ds_mcc_train"
METRIC_DATASHIFT_MCC_ALL = "ds_mcc_all"
# new key names with debug postfix
DEBUG_DATASHIFT_MCC_TEST = "mcc_test_for_debug"
DEBUG_DATASHIFT_MCC_TRAIN = "mcc_train_for_debug"
DEBUG_DATASHIFT_MCC_ALL = "mcc_all_for_debug"

METRIC_DATASHIFT_FEATURE_IMPORTANCE = "ds_feature_importance"
METRIC_STATISTICAL_DISTANCE_WASSERSTEIN = "wasserstein_distance"
METRIC_STATISTICAL_DISTANCE_ENERGY = "energy_distance"
METRIC_DATASET_METRICS = "dataset_metrics"
METRIC_COLUMN_METRICS = "column_metrics"
METRIC_TYPE = "metric_type"
METRIC_TYPE_DATASET = "dataset"
METRIC_TYPE_COLUMN = "column"

LOG_FLUSH_LATENCY = 60
EMAIL_ADDRESSES = "email_addresses"

COLUMN_NAME = "column_name"
MODEL_NAME = "model_name"
MODEL_VERSION = "model_version"
SERVICE_NAME = "service_name"
SERVICE = "service"
DRIFT_THRESHOLD = "drift_threshold"
DATETIME = "datetime"
HAS_DRIFT = "has_drift"
RUN_ID = "runid"
SCORING_DATE = "scoring_date"
PIPELINE_START_TIME = "pipeline_starttime"

RUN_TYPE_ADHOC = "Adhoc"
RUN_TYPE_SCHEDULE = "Scheduler"

PIPELINE_PARAMETER_ADHOC_RUN = "pipeline_arg_adhoc_run"

FIGURE_FEATURE_IMPORTANCE_TITLE = "Drift Contribution by Feature\n"
FIGURE_FEATURE_IMPORTANCE_Y_LABEL = "Drift Contribution"

CURATION_COL_NAME_CORRELATIONID = "$CorrelationId"
CURATION_COL_NAME_TIMESTAMP = "$Timestamp"
CURATION_COL_NAME_TIMESTAMP_CURATION = "$Timestamp_Curation"
CURATION_COL_NAME_TIMESTAMP_INPUTS = "$Timestamp_Inputs"
CURATION_COL_NAME_TIMESTAMP_PREDICTIONS = "$Timestamp_Predictions"
CURATION_COL_NAME_REQUESTID = "$RequestId"
CURATION_COL_NAME_REQUESTID_INPUTS = "$RequestId_Inputs"
CURATION_COL_NAME_REQUESTID_PREDICTIONS = "$RequestId_Predictions"
CURATION_COL_NAME_FEATURES = "$Features"
CURATION_COL_NAME_PREDCTION_RESULT = "$Prediction_Result"
CURATION_COL_NAME_MODELNAME = "$ModelName"
CURATION_COL_NAME_MODELVERSION = "$ModelVersion"
CURATION_COL_NAME_SERVICENAME = "$ServiceName"
CURATION_COL_NAME_LABELDATAISAVAILABLE = "$LabelDataIsAvailable"
CURATION_COL_NAME_SIGNALDATAISAVAILABLE = "$SignalDataIsAvailable"

SCRIPT_DATABRICKS_INIT = "/databricks/init_datadrift/install.sh"
COMPUTE_TARGET_TYPE_AML = "AmlCompute"
COMPUTE_TARGET_TYPE_DATABRICKS = "Databricks"

OUTPUT_METRIC_DRIFT_COEFFICIENT = "datadrift_coefficient"
OUTPUT_METRIC_DRIFT_CONTRIBUTION = "datadrift_contribution"
