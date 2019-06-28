# #######
# This file is designed to help with logging metrics to Google's Stackdriver.
#
# #######

import google
from google.auth.transport import requests
from google.oauth2 import service_account
from google.cloud import monitoring_v3
from google.protobuf.timestamp_pb2 import Timestamp

import os
import time


def create_descriptor(descriptor_info, project):
    try:
        credentials, project = google.auth.default()

    # this is just for local testing
    except:
        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

    client = monitoring_v3.MetricServiceClient(credentials=credentials)
    name = client.project_path(project)

    metric_descriptor = create_descriptor_dict(descriptor_info)

    return client.create_metric_descriptor(name, metric_descriptor)


def log_point(series_info, project):
    try:
        credentials, project = google.auth.default()

    # this is just for local testing
    except:
        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

    client = monitoring_v3.MetricServiceClient(credentials=credentials)
    project_name = client.project_path(project)

    series = create_time_series_dict(series_dict=series_info)

    return client.create_time_series(project_name, [series])


def create_time_series_dict(series_dict):
    now = time.time()

    for required_key in ['metric', 'resource']:

        if required_key not in series_dict.keys():

            raise Exception('The required key ' + required_key + ' is not in the series dict provided:\n' + str(series_dict))

    default_dict = {
        "metric": {
            "type": "custom.googleapis.com/",
            "labels": {}
        },
        "resource": {
            "type": "generic_task",
            "labels": {
                "job": "",
                "location": "",
                "namespace": "",
                "task_id": ""
            }
        },
        "metadata": {},
        "metric_kind": "CUMULATIVE",
        "value_type": "DOUBLE",
        "points": [
            {
                "interval": {
                    "start_time": Timestamp(seconds=int(now), nanos=int((now - int(now)) * 10**9)),
                    "end_time": Timestamp(seconds=int(now)+1, nanos=int((now - int(now)) * 10**9))
                },
                "value": {
                    "double_value": 1.0
                }
            }
        ]
    }

    default_dict.update(series_dict)

    return default_dict


def create_descriptor_dict(description_dict):

    for required_key in ['name', 'display_name', 'type']:

        if required_key not in description_dict.keys():

            raise Exception('The required key ' + required_key + ' is not in the dictionary provided:\n' + str(description_dict))

    default = {
        "name": "projects/",
        "description": "",
        "display_name": "",
        "type": "",
        "metric_kind": "CUMULATIVE",
        "value_type": "DOUBLE",
        "labels": [],
    }

    default.update(description_dict)
    return default


TASK_DURATION_METRIC_TYPE = 'custom.googleapis.com/airflow/extensions/task_duration/1.2'
TASK_CALLBACK_METRIC_TYPE = 'custom.googleapis.com/airflow/extensions/task_callback/1.0'

def get_total_time_dict_from_context(google_project_name, task_key, label_list=None):
    return {
        "name": "projects/" + google_project_name,
        "description": "Task Duration",
        "display_name": "log_duration",
        "type": TASK_DURATION_METRIC_TYPE,
        "metric_kind": "GAUGE",
        "value_type": "INT64",
        "labels": label_list if label_list is not None else [],
    }


def get_callback_metric_dict(google_project_name, label_list=None):
    return {
        "name": "projects/" + google_project_name,
        "description": "Task Callback",
        "display_name": "task_callback",
        "type": TASK_CALLBACK_METRIC_TYPE,
        "metric_kind": "CUMULATIVE",
        "value_type": "INT64",
        "labels": label_list if label_list is not None else [],
    }


def get_point_dict_from_context(google_location, time_delta, task_key, label_values=None):
    now = time.time()

    return {
        "metric": {
            "type": TASK_DURATION_METRIC_TYPE,
            "labels": label_values if label_values is not None else {},
        },
        "resource": {
            "type": "generic_task",
            "labels": {
                "job": "extensions",
                "location": google_location,
                "namespace": "log_duration",
                "task_id": task_key
            }
        },
        "metadata": {},
        "metric_kind": "GAUGE",
        "value_type": "INT64",
        "points": [
            {
                "interval": {
                    "start_time": Timestamp(seconds=int(now), nanos=int((now - int(now)) * 10 ** 9)),
                    "end_time": Timestamp(seconds=int(now), nanos=int((now - int(now)) * 10 ** 9))
                },
                "value": {
                    "int64_value": time_delta
                }
            }
        ]
    }


def get_callback_point_dict(google_location, callback_type, task_key, point_value=1, label_values=None):
    now = time.time()

    return {
        "metric": {
            "type": TASK_CALLBACK_METRIC_TYPE,
            "labels": label_values if label_values is not None else {},
        },
        "resource": {
            "type": "generic_task",
            "labels": {
                "job": "extensions",
                "location": google_location,
                "namespace": "log_callback_" + callback_type,
                "task_id": task_key,
            }
        },
        "metadata": {},
        "metric_kind": "CUMULATIVE",
        "value_type": "INT64",
        "points": [
            {
                "interval": {
                    "start_time": Timestamp(seconds=int(now) - 1, nanos=int((now - int(now)) * 10 ** 9)),
                    "end_time": Timestamp(seconds=int(now), nanos=int((now - int(now)) * 10 ** 9))
                },
                "value": {
                    "int64_value": point_value
                }
            }
        ]
    }

