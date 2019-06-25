# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import time
import os
import uuid

from datetime import datetime, timedelta
from azureml.core.run import Run
from azureml.contrib.datadrift import datadriftdetector as dd
from azureml.contrib.datadrift._logging._metric_logger import _MetricLogger
from azureml.contrib.datadrift._logging._telemetry_logger import _TelemetryLogger, INSTRUMENTATION_KEY
from azureml.contrib.datadrift._logging._telemetry_logger_context_filter import _TelemetryLoggerContextFilter
from azureml.contrib.datadrift._utils.constants import LOG_FLUSH_LATENCY, RUN_TYPE_SCHEDULE, RUN_TYPE_ADHOC
from azureml.contrib.datadrift._utils.constants import (
    CURATION_COL_NAME_CORRELATIONID, CURATION_COL_NAME_TIMESTAMP, CURATION_COL_NAME_TIMESTAMP_CURATION,
    CURATION_COL_NAME_TIMESTAMP_INPUTS, CURATION_COL_NAME_TIMESTAMP_PREDICTIONS, CURATION_COL_NAME_REQUESTID,
    CURATION_COL_NAME_REQUESTID_INPUTS, CURATION_COL_NAME_REQUESTID_PREDICTIONS, CURATION_COL_NAME_FEATURES,
    CURATION_COL_NAME_MODELNAME, CURATION_COL_NAME_MODELVERSION, CURATION_COL_NAME_SERVICENAME,
    CURATION_COL_NAME_LABELDATAISAVAILABLE, CURATION_COL_NAME_SIGNALDATAISAVAILABLE, CURATION_COL_NAME_PREDCTION_RESULT
)
from azureml.contrib.datadrift._datadiff import Metric

import pyspark
from pyspark import SparkConf
from pyspark.sql.functions import lit, col, create_map
from pyspark.sql.utils import AnalysisException
from itertools import chain


module_logger = _TelemetryLogger.get_telemetry_logger('_generate_script_datacuration_pyspark')


def main():
    parser = argparse.ArgumentParser("script")

    parser.add_argument("--scoring_data", type=str, help="Training Data Reference Object")
    parser.add_argument("--predictions_data", type=str, help="Scoring Data Reference Object")
    parser.add_argument("--model_serving_output_path", type=str, help="Model serving output path")
    parser.add_argument("--workspace_name", type=str, help="Workspace name")
    parser.add_argument("--workspace_location", type=str, help="Workspace location")
    parser.add_argument("--model_name", type=str, help="Model name")
    parser.add_argument("--model_version", type=str, help="Model version")
    parser.add_argument("--service", type=str, help="Deployed service name")
    parser.add_argument("--pipeline_name", type=str, help="Deployed pipeline name")
    parser.add_argument("--root_correlation_id", type=str, help="Caller correlation Id")
    parser.add_argument("--instrumentation_key", type=str, help="Application insight instrumentation key")
    parser.add_argument("--version", type=str, help="Pipeline version")
    parser.add_argument("--subscription_id", type=str, help="Subscription Id")
    parser.add_argument("--resource_group", type=str, help="Resource Group")
    parser.add_argument("--enable_metric_logger", type=bool, default=False, help="Enable metrics logger")
    parser.add_argument("--latency_in_days", type=int, default=1, help="latency in days")
    parser.add_argument("--target_date", type=str, help="Target date of the data. The format should be YYYY-MM-DD")
    parser.add_argument("--adhoc_run", type=str, default=RUN_TYPE_SCHEDULE, help="adhoc run")
    parser.add_argument("--local_run", type=bool, default=False, help="local run")

    # arguments from the pipeline
    parser.add_argument("--init_finished", type=str, help="init script finished")
    parser.add_argument("--ModelServing", type=str, help="Model Serving")
    parser.add_argument("--AZUREML_SCRIPT_DIRECTORY_NAME", type=str, help="Model Serving")
    parser.add_argument("--AZUREML_RUN_TOKEN", type=str, help="Model Serving")
    parser.add_argument("--AZUREML_RUN_ID", type=str, help="Model Serving")
    parser.add_argument("--AZUREML_ARM_SUBSCRIPTION", type=str, help="Model Serving")
    parser.add_argument("--AZUREML_ARM_RESOURCEGROUP", type=str, help="Model Serving")
    parser.add_argument("--AZUREML_ARM_WORKSPACE_NAME", type=str, help="Model Serving")
    parser.add_argument("--AZUREML_ARM_PROJECT_NAME", type=str, help="Model Serving")

    args = parser.parse_args()
    run = Run.get_context(allow_offline=args.local_run)
    adhoc_run = (args.adhoc_run == RUN_TYPE_ADHOC)

    if args.local_run:
        spark = pyspark.sql.SparkSession.builder.master("local").config(conf=SparkConf()).getOrCreate()
    else:
        spark = pyspark.sql.SparkSession.builder.appName('DataDriftDetector').getOrCreate()

    try:
        runid = run.get_details()["runId"]
    except AttributeError:
        runid = "{}".format(uuid.uuid4())
    runid = "{}".format(uuid.uuid4())

    log_context = {'workspace_name': args.workspace_name, 'model_name': args.model_name,
                   'model_version': args.model_version, 'service': args.service, 'pipeline_name': args.pipeline_name,
                   'pipeline_version': args.version, 'root_correlation_id': args.root_correlation_id, 'run_id': runid,
                   'subscription_id': args.subscription_id, 'resource_group': args.resource_group,
                   'run_type': RUN_TYPE_ADHOC if adhoc_run else RUN_TYPE_SCHEDULE,
                   'local_run': args.local_run, 'workspace_location': args.workspace_location}

    module_logger.addFilter(_TelemetryLoggerContextFilter(log_context))
    curation_time = datetime.utcnow()

    try:
        with _TelemetryLogger.log_activity(module_logger,
                                           activity_name="_generate_script_datacuration_pyspark") as logger:
            logger.info("In script.py, runid:{}".format(runid))

            for arg in vars(args):
                logger.debug("{}: {}".format(arg, getattr(args, arg)))

            # if target_date is specified, use it as target date. Otherwise, switch to use (utcnow - latency_in_days)
            if args.target_date:
                target_date = datetime.strptime(args.target_date, '%Y-%m-%d')
            else:
                target_date = curation_time - timedelta(days=args.latency_in_days)

            # set up metric logger
            if args.enable_metric_logger:
                metric_logger = _MetricLogger(INSTRUMENTATION_KEY)
                extended_properties = {'target_date': target_date.strftime("%Y-%m-%d"),
                                       'model_name': args.model_name,
                                       'model_version': args.model_version,
                                       'service': args.service,
                                       'pipeline_name': args.pipeline_name,
                                       'runid': runid,
                                       'run_type': RUN_TYPE_ADHOC if adhoc_run else RUN_TYPE_SCHEDULE}

            # read and process inputs(scoring) data
            if adhoc_run:
                scoring_data_path = args.scoring_data
            else:
                scoring_data_path = os.path.join("{}{}".format(args.scoring_data, target_date.strftime('%Y')),
                                                 target_date.strftime('%m'), target_date.strftime('%d'),
                                                 "data.csv")
            try:
                inputs = spark.read.format("csv") \
                                   .option("inferSchema", "false") \
                                   .option("header", "true") \
                                   .option("sep", ",") \
                                   .load(scoring_data_path)
            except AnalysisException:
                logger.error("Scording data is not found at {}".format(scoring_data_path))
                return 0
            except KeyError as e:
                logger.error("Scoring data is malformed")
                logger.error(e, exc_info=True)
                return 0

            inputs = inputs.withColumnRenamed(CURATION_COL_NAME_TIMESTAMP, CURATION_COL_NAME_TIMESTAMP_INPUTS) \
                           .withColumnRenamed(CURATION_COL_NAME_REQUESTID, CURATION_COL_NAME_REQUESTID_INPUTS)

            features = create_map(list(chain(*(
                                  (lit(name), col(name)) for name in inputs.columns if "$" not in name
                                  )))).alias(CURATION_COL_NAME_FEATURES)
            inputs = inputs.select(CURATION_COL_NAME_CORRELATIONID,
                                   CURATION_COL_NAME_REQUESTID_INPUTS,
                                   CURATION_COL_NAME_TIMESTAMP_INPUTS,
                                   features)

            rowcount_scoring = inputs.count()
            logger.debug("Scoring data row count:{}".format(rowcount_scoring))
            logger.debug("Scoring data schema:{}".format(inputs.dtypes))
            if args.enable_metric_logger:
                metric_logger.log_metric(Metric(name='rowcount_scoring',
                                                value=rowcount_scoring,
                                                extended_properties=extended_properties))

            # read and process predictions data
            if adhoc_run:
                predictions_data_path = args.predictions_data
            else:
                predictions_data_path = os.path.join("{}{}".format(args.predictions_data, target_date.strftime('%Y')),
                                                     target_date.strftime('%m'), target_date.strftime('%d'),
                                                     "data.csv")
            try:
                predictions = spark.read.format("csv") \
                                        .option("inferSchema", "false") \
                                        .option("header", "true") \
                                        .load(predictions_data_path)
            except AnalysisException:
                logger.error("Predictions data is not found at {}".format(predictions_data_path))
                return 0
            except KeyError as e:
                logger.error("Predictions data is malformed")
                logger.error(e, exc_info=True)
                return 0

            rowcount_predictions = predictions.count()
            logger.debug("Predictions data row count:{}".format(rowcount_predictions))
            logger.debug("Predictions data schema:{}".format(predictions.dtypes))
            if args.enable_metric_logger:
                metric_logger.log_metric(Metric(name='rowcount_predictions',
                                                value=rowcount_predictions,
                                                extended_properties=extended_properties))

            # filter out rows with null corrleation id
            predictions = predictions.na.drop(subset=[CURATION_COL_NAME_CORRELATIONID])
            # do de-duplication on correlation id
            predictions = predictions.dropDuplicates(subset=[CURATION_COL_NAME_CORRELATIONID])

            rowcount_predictions_filtered = predictions.count()
            logger.debug("Prediction data after flitering and dedup row count:{}"
                         .format(rowcount_predictions_filtered))
            if args.enable_metric_logger:
                metric_logger.log_metric(Metric(name='rowcount_predictions_filtered',
                                                value=rowcount_predictions_filtered,
                                                extended_properties=extended_properties))

            predictions = predictions.withColumnRenamed(CURATION_COL_NAME_TIMESTAMP,
                                                        CURATION_COL_NAME_TIMESTAMP_PREDICTIONS) \
                                     .withColumnRenamed(CURATION_COL_NAME_REQUESTID,
                                                        CURATION_COL_NAME_REQUESTID_PREDICTIONS)
            prediction_result = create_map(list(chain(*(
                                           (lit(name), col(name)) for name in predictions.columns if "$" not in name
                                           )))).alias(CURATION_COL_NAME_PREDCTION_RESULT)
            predictions = predictions.select(CURATION_COL_NAME_CORRELATIONID, CURATION_COL_NAME_REQUESTID_PREDICTIONS,
                                             CURATION_COL_NAME_TIMESTAMP_PREDICTIONS, prediction_result)

            # join inputs and predictions to get model serving data
            serving_data = inputs.join(predictions, CURATION_COL_NAME_CORRELATIONID, 'LeftOuter')
            serving_data = serving_data.withColumn(CURATION_COL_NAME_TIMESTAMP_CURATION,
                                                   lit(curation_time.strftime('%Y-%m-%dT%H:%M:%S.%f')))
            serving_data = serving_data.withColumn(CURATION_COL_NAME_MODELNAME, lit(args.model_name))
            serving_data = serving_data.withColumn(CURATION_COL_NAME_MODELVERSION, lit(args.model_version))
            serving_data = serving_data.withColumn(CURATION_COL_NAME_SERVICENAME, lit(args.service))

            # added columns that indicate the availability of label data and signal data
            serving_data = serving_data.withColumn(CURATION_COL_NAME_LABELDATAISAVAILABLE, lit(False))
            serving_data = serving_data.withColumn(CURATION_COL_NAME_SIGNALDATAISAVAILABLE, lit(False))

            rowcount_serving = serving_data.count()
            logger.debug("Model serving data row count:{}".format(rowcount_serving))
            logger.debug("Model serving data schema:{}".format(serving_data.dtypes))
            if args.enable_metric_logger:
                metric_logger.log_metric(Metric(name='rowcount_serving',
                                                value=rowcount_serving,
                                                extended_properties=extended_properties))

            model_serving_output_path_root = args.ModelServing
            if adhoc_run:
                model_serving_output_path = args.model_serving_output_path
            else:
                model_serving_output_path = dd.DataDriftDetector._get_model_serving_path(args.model_name,
                                                                                         args.model_version,
                                                                                         args.service,
                                                                                         target_date)
            model_serving_output = os.path.join(model_serving_output_path_root,
                                                model_serving_output_path)

            logger.debug("Model serving data output path is:{}".format(model_serving_output))
            logger.debug("Creating output metrics directory if not exist: {}"
                         .format(os.path.dirname(model_serving_output)))
            os.makedirs(os.path.dirname(model_serving_output), exist_ok=True)

            serving_data.write.mode('overwrite').parquet(model_serving_output)
    except KeyError as e:
        # scoring data or predictions data is malformed.
        # exit rather than fail to let the other curation and drift steps run.
        logger.error(e, exc_info=True)
        return 0
    except Exception as e:
        # failed due to unexpected exception. raise the exception.
        logger.error(e, exc_info=True)
        raise
    finally:
        # allow time for async channel to send the service log entities to application insights
        if module_logger.handlers:
            for handler in module_logger.handlers:
                handler.flush()
                if type(handler).__name__ == 'AppInsightsLoggingHandler':
                    print('Wait some time for application insights async channel to flush')
                    time.sleep(LOG_FLUSH_LATENCY)


if __name__ == '__main__':
    main()
