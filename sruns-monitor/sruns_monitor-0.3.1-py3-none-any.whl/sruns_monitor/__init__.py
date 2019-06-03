# -*- coding: utf-8 -*-

import os

from ._logging import *

#: The JSON Schema file that defines the properties of the configuration file.
CONF_SCHEMA = os.path.join(os.path.dirname(__file__), "schema.json")
#: Configuration parameter names in conf.json. Each of the variables that starts with a C_ denotes
#: a config parameter. 
C_WATCHDIR = "watchdir"
C_COMPLETED_RUNS_DIR = "completed_runs_dir"
C_SQLITE_DB = "sqlite_db"
C_FIRESTORE_COLLECTION = "firestore_collection"
C_GCP_BUCKET_NAME = "gcp_bucket_name"
C_GCP_BUCKET_BASEDIR = "gcp_bucket_basedir"
C_CYCLE_PAUSE_SEC = "cycle_pause_sec"
C_TASK_RUNTIME_LIMIT_SEC = "task_runtime_limit_sec"

# Attribute names for Firestore database
FIRESTORE_ATTR_RUN_NAME = "name"
#: The status of the workflow. Possible values are provided by the 
#: `sruns_monitor.monitor.Monitor.RUN_STATUS_*` attributes.
FIRESTORE_ATTR_WF_STATUS = "workflow_status"
#: Bucket storage object path for the tarred run directory in the form bucket_name/path/to/run.tar.gz.
FIRESTORE_ATTR_STORAGE = "storage" 
