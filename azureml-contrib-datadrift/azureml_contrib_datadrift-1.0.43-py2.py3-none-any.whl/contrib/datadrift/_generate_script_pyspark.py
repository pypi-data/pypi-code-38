# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import os
import sys
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import jsonpickle
import numpy as np
import pandas as pd
from azureml.contrib.datadrift import _datadiff as dd
from azureml.contrib.datadrift import datadriftdetector
from azureml.contrib.datadrift._logging._metric_logger import _MetricLogger
from azureml.contrib.datadrift._logging._telemetry_logger import \
    _TelemetryLogger
from azureml.contrib.datadrift._logging._telemetry_logger_context_filter import \
    _TelemetryLoggerContextFilter
from azureml.contrib.datadrift._utils import pdutils
from azureml.contrib.datadrift._utils.constants import (LOG_FLUSH_LATENCY,
                                                        RUN_TYPE_ADHOC,
                                                        RUN_TYPE_SCHEDULE)
from azureml.core import Datastore
from azureml.core.dataset import Dataset
from azureml.core.model import Model
from azureml.core.run import Run
from azureml.data.dataset_snapshot import DatasetSnapshot

module_logger = _TelemetryLogger.get_telemetry_logger('gen_script')
pipeline_starttime = datetime.utcnow()


def get_distributions(pd_dataset, decimal=3):
    distributions = []

    for column in pd_dataset:
        if pd.api.types.is_numeric_dtype(pd_dataset[column].dtype):
            binlabel, weight = np.unique(np.around(pd_dataset[column].values, decimal), return_counts=True)
            distributions.append(dd.Distribution(column, binlabel, weight))

    return distributions


def run_datadiff(base_ds, diff_ds, logger, include_columns=None):
    if include_columns is None or len(include_columns) == 0:
        columns = base_ds.columns & diff_ds.columns
        logger.debug("Common columns:{}".format(", ".join(columns)),
                     extra={'properties':
                            {"common_col_counts": len(columns)}
                            })
    else:
        columns = include_columns
        logger.debug("Whitelisted columns:{}".format(", ".join(include_columns)),
                     extra={'properties':
                            {"whitelist_col_counts": len(include_columns)}
                            })

    base_processed, diff_processed = get_preprocessed_dfs(
        base_ds[columns], diff_ds[columns], logger)

    assert len(base_processed.columns) != 0, "No columns are available for diff calculation."

    logger.debug("Columns eligible for diff: {}".format(", ".join(base_processed.columns)),
                 extra={'properties':
                        {"diff_col_counts": len(base_processed.columns)}
                        })

    base_distribution = get_distributions(base_processed)
    diff_distribution = get_distributions(diff_processed)
    ddo = dd.DataDiff(base_processed, diff_processed, base_distribution, diff_distribution)
    metrics = ddo.run()
    ds_model = ddo.model_dict["ds_model"]
    return metrics, ds_model


def get_preprocessed_dfs(base, diff, logger):
    common_columns = base.columns & diff.columns

    dfsummaries_base = pdutils.get_pandas_df_summary(base[common_columns])
    dfsummaries_diff = pdutils.get_pandas_df_summary(diff[common_columns])

    columns_to_drop = list(set(pdutils.get_inferred_drop_columns(dfsummaries_base)).union(
        set(pdutils.get_inferred_drop_columns(dfsummaries_diff))))

    base_fillna_columns = pdutils.get_inferred_fillna_columns(dfsummaries_base)
    diff_fillna_columns = pdutils.get_inferred_fillna_columns(dfsummaries_diff)

    common_columns_filtered = list(set(common_columns) - set(columns_to_drop))

    categorical_columns = list(set(pdutils.get_inferred_categorical_columns(dfsummaries_base)).intersection(
        common_columns_filtered))

    logger.info("Columns to be dropped from comparision due to high invalid "
                "value counts from either or both of datasets: {}"
                .format(", ".join(columns_to_drop)),
                extra={'properties':
                       {"drop_col_counts": len(columns_to_drop)}
                       })

    logger.info("Columns treated as categorical columns base on baseline dataset: {}"
                .format(", ".join(categorical_columns)),
                extra={'properties':
                       {"cat_col_counts": len(categorical_columns)}
                       })

    logger.info("Columns treated with fillna with mean for base dataset: {}"
                .format(", ".join(base_fillna_columns)),
                extra={'properties':
                       {"base_fillna_col_counts": len(base_fillna_columns)}
                       })

    logger.info("Columns treated with fillna with mean for diff dataset: {}"
                .format(", ".join(diff_fillna_columns)),
                extra={'properties':
                       {"diff_fillna_col_counts": len(diff_fillna_columns)}
                       })

    for c in categorical_columns:
        common_cats = list(set(np.concatenate((base[c].unique(), diff[c].unique()))))
        cat_type = pd.api.types.CategoricalDtype(categories=common_cats)
        base[c] = base[c].astype(cat_type)
        diff[c] = diff[c].astype(cat_type)

    base[base_fillna_columns] = base[base_fillna_columns].fillna(base[base_fillna_columns].mean())
    diff[diff_fillna_columns] = diff[diff_fillna_columns].fillna(diff[diff_fillna_columns].mean())

    return base[common_columns_filtered], diff[common_columns_filtered]


def get_scoring_path(arg_scoring, is_adhoc_run, target_date):
    if is_adhoc_run:
        scoring_dataset_path = Path(arg_scoring)

    else:
        scoring_dataset_path = Path(os.path.join("{}{}".format(arg_scoring, target_date.strftime('%Y')),
                                    target_date.strftime('%m'), target_date.strftime('%d'),
                                    "data.csv"))

    scoring_profile_path = Path(os.path.join(str(scoring_dataset_path.parent), "profile.json"))

    return scoring_dataset_path, scoring_profile_path


def get_training_profile_path(arg_scoring, sub_id, res_group, ws_name, model_name, model_version):
    prefix = Path(arg_scoring)
    rel_path = Path("{}/{}/{}".format(sub_id, res_group, ws_name))

    profile_path = None

    for i in prefix.parents:
        if str(i).endswith(str(rel_path)):
            profile_path = Path(os.path.join(str(i), "{}_{}_training_profile.json".format(model_name, model_version)))

    return profile_path


def main():
    parser = argparse.ArgumentParser("script")

    parser.add_argument("--training_data", type=str, help="Training Data Reference Object")
    parser.add_argument("--scoring_data", type=str, help="Scoring Data Reference Object")
    parser.add_argument("--metrics_output_path_root", type=str, help="Metric output path root")
    parser.add_argument("--metrics_output_path", type=str, help="Metric output path")
    parser.add_argument("--workspace_name", type=str, help="Workspace name")
    parser.add_argument("--workspace_location", type=str, help="Workspace location")
    parser.add_argument("--model_name", type=str, help="Model name")
    parser.add_argument("--model_version", type=int, help="Model version")
    parser.add_argument("--service", type=str, help="Deployed service name")
    parser.add_argument("--pipeline_name", type=str, help="Deployed pipeline name")
    parser.add_argument("--root_correlation_id", type=str, help="Caller correlation Id")
    parser.add_argument("--instrumentation_key", type=str, help="Application insight instrumentation key")
    parser.add_argument("--latency_in_days", type=int, default=1, help="latency in days")
    parser.add_argument("--target_date", type=str, help="Target date of the data. The format should be YYYY-MM-DD")
    parser.add_argument("--end_date", type=str, help="End date of the scoring data")
    parser.add_argument("--version", type=str, help="Pipeline version")
    parser.add_argument("--subscription_id", type=str, help="Subscrption Id")
    parser.add_argument("--enable_metric_logger", type=bool, default=False, help="Enable metrics logger")
    parser.add_argument("--adhoc_run", type=str, default=RUN_TYPE_SCHEDULE, help="adhoc run")
    parser.add_argument("--drift_threshold", type=float, default=0.2, help="drift threshold")
    parser.add_argument("--features_whitelist", nargs='*', default=[], help="feature whitelist")
    parser.add_argument("--datadrift_id", type=str, help="Datadrift object id")
    parser.add_argument("--local_run", type=bool, default=False, help="local run")

    parser.add_argument("--init_finished", type=str, help="init script finished")
    parser.add_argument("--DataDrift", type=str, help="Datadrift object id")
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

    if not args.local_run:
        runid = run.get_details()["runId"]
        ws = run.experiment.workspace
        ds = Datastore(ws, "workspaceblobstore")
    else:
        runid = "{}".format(uuid.uuid4())

    log_context = {'workspace_name': args.workspace_name, 'model_name': args.model_name,
                   'model_version': args.model_version, 'service': args.service, 'pipeline_name': args.pipeline_name,
                   'pipeline_version': args.version, 'root_correlation_id': args.root_correlation_id, 'run_id': runid,
                   'subscription_id': args.subscription_id, 'datadrift_id': args.datadrift_id,
                   'run_type': RUN_TYPE_ADHOC if adhoc_run else RUN_TYPE_SCHEDULE,
                   'workspace_location': args.workspace_location}

    module_logger.addFilter(_TelemetryLoggerContextFilter(log_context))
    curation_time = datetime.utcnow()
    module_logger.info("At {} _generate_script_pyspark.py called with the following argument list: {}".format(
        pipeline_starttime, sys.argv))

    try:
        with _TelemetryLogger.log_activity(module_logger, activity_name="gen_script") as logger:
            logger.info("In script.py, runid:{}".format(runid))

            for arg in vars(args):
                logger.debug("{}: {}".format(arg, getattr(args, arg)))

            if args.training_data:
                # read training data in local. for local test only
                training = Dataset.from_delimited_files(path=args.training_data, separator=',')
                trainpd = training.to_pandas_dataframe()
            else:
                # Try to read training data from the dataset snapshot
                logger.debug("Try to read training data from dataset snapshot")
                ws = run.experiment.workspace
                model = Model(ws, name=args.model_name, version=args.model_version)

                training = model.datasets[Dataset.Scenario.TRAINING]
                if not training:
                    raise Exception("No training Dataset or DatasetSnapshot is registed with the model")
                elif len(training) > 1:
                    logger.warning("More than one training Dataset/Snapshot is registered, using the first one")

                training = training[0]

                if isinstance(training, DatasetSnapshot):
                    logger.debug("Reading the training data from a DatasetSnapshot")
                elif isinstance(training, Dataset):
                    logger.debug("Reading the training data from a Dataset")
                else:
                    raise TypeError("Training data must be a DatasetSnapshot or a Dataset")
                trainpd = training.to_pandas_dataframe()
                logger.debug("Successfully read the training data")

            # if target_date is specified, use it as target date. Otherwise, switch to use (utcnow - latency_in_days)
            if args.target_date:
                target_date = datetime.strptime(args.target_date, '%Y-%m-%d')
            else:
                target_date = curation_time - timedelta(days=args.latency_in_days)

            scoringpd_path, scoring_profile_path = get_scoring_path(args.scoring_data, adhoc_run, target_date)

            logger.debug("Reading scoring data from {}".format(str(scoringpd_path)))

            scoring_ds = Dataset.from_delimited_files(path=str(scoringpd_path), separator=',')
            with open(str(scoring_profile_path), "w") as f:
                f.write(scoring_ds.get_profile(
                    arguments={
                        'number_of_histogram_bins': 1000
                    }
                )._to_json())
                logger.debug("Scoring profile {} written.".format(str(scoring_profile_path)))

            scoringpd = scoring_ds.to_pandas_dataframe()

            # Remove GUID generated by azureml pipelinedata.
            if args.local_run:
                metrics_output_path_root = str(Path(args.metrics_output_path_root).parents[1])
            else:
                metrics_output_path_root = tempfile.gettempdir()

            if adhoc_run:
                metrics_output_path = args.metrics_output_path
            else:
                metrics_output_path = datadriftdetector.DataDriftDetector._get_metrics_path(
                    args.model_name, args.model_version, args.service, target_date)
            metrics_output = os.path.join(metrics_output_path_root, metrics_output_path,
                                          "output_{}.json".format(runid))

            logger.debug("Training input schema:")
            logger.debug("{}".format(trainpd.dtypes))

            logger.debug("Scoring input schema:")
            logger.debug("{}".format(scoringpd.dtypes))

            metrics, ds_model = run_datadiff(base_ds=trainpd, diff_ds=scoringpd,
                                             logger=logger, include_columns=args.features_whitelist)

            logger.debug("Metric output file absolute path is: {}".format(os.path.abspath(metrics_output)))

            logger.debug("Creating output metrics directory if not exist: {}".format(os.path.dirname(metrics_output)))
            os.makedirs(os.path.dirname(metrics_output), exist_ok=True)

            for m in metrics:
                m.add_extended_properties({
                    'scoring_date': target_date,
                    'model_name': args.model_name,
                    'model_version': args.model_version,
                    'service': args.service,
                    'pipeline_name': args.pipeline_name,
                    'runid': runid,
                    'drift_threshold': args.drift_threshold,
                    'pipeline_starttime': pipeline_starttime,
                    'run_type': RUN_TYPE_ADHOC if adhoc_run else RUN_TYPE_SCHEDULE,
                    'datadrift_id': args.datadrift_id
                })

            try:
                for m in metrics:
                    logger.debug("{}".format(m))
            except AttributeError:
                logger.debug("Could not print metrics")

            with open(metrics_output, "w") as f:
                f.write(jsonpickle.encode(metrics))

            if not args.local_run:
                ds.upload_files(files=[os.path.abspath(metrics_output)],
                                target_path=metrics_output_path,
                                show_progress=False)

            if args.enable_metric_logger:
                metric_logger = _MetricLogger(args.instrumentation_key)

                for m in metrics:
                    metric_logger.log_metric(m)

                logger.info('{} metrics logged'.format(str(len(metrics))))
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
