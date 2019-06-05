# -*- coding: utf-8 -*-

import os

from ._logging import *

#: The JSON Schema file that defines the properties of the configuration file.
CONF_SCHEMA = os.path.join(os.path.dirname(__file__), "schema.json")
#: Configuration parameter names in conf.json. Each of the variables that starts with a `C_` denotes
#: a config parameter. 
C_WATCHDIR = "watchdir"
#: JSON configuration parameter name for specifying the mail configuration object.
C_MAIL = "mail"
#: JSON configuration parameter name for specifying the location of the completed runs directory.
C_COMPLETED_RUNS_DIR = "completed_runs_dir"
#: JSON configuration parameter name for specifying how long a directory in the completed runs location
#: can exist for prior to being deleted.
C_SWEEP_AGE_SEC = "sweep_age_sec"
#: JSON configuration parameter name for specifying the name of the SQLite database.
C_SQLITE_DB = "sqlite_db"
#: JSON configuration parameter name for specifying the Firestore collection. 
C_FIRESTORE_COLLECTION = "firestore_collection"
#: JSON configuration parameter name for specifying the Google Storage bucket name. 
C_GCP_BUCKET_NAME = "gcp_bucket_name"
#: JSON configuration parameter name for specifying the folder to write to in the Google bucket. 
C_GCP_BUCKET_BASEDIR = "gcp_bucket_basedir"
#: JSON configuration parameter name for specifying how long to pause between monitor scans.
C_CYCLE_PAUSE_SEC = "cycle_pause_sec"
#: JSON configuration parameter name for specifying how long a child prcocess can run. 
C_TASK_RUNTIME_LIMIT_SEC = "task_runtime_limit_sec"

# Attribute names for Firestore database
FIRESTORE_ATTR_RUN_NAME = "name"
#: The status of the workflow. Possible values are provided by the 
#: `sruns_monitor.monitor.Monitor.RUN_STATUS_*` attributes.
FIRESTORE_ATTR_WF_STATUS = "workflow_status"
#: Bucket storage object path for the tarred run directory in the form bucket_name/path/to/run.tar.gz.
FIRESTORE_ATTR_STORAGE = "storage" 
