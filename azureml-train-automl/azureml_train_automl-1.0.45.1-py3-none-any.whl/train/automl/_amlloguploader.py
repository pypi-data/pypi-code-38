# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for uploading aml log files."""
import os

from azureml._history.utils.constants import (AZUREML_LOGS, AZUREML_LOG_FILE_NAME)
from azureml._logging.debug_mode import diagnostic_log

from azureml.core import Run
from .run import AutoMLRun


class _AMLLogUploader():
    def __init__(self, run, worker_id):
        self.run = run
        self.worker_id = str(worker_id)
        AZUREML_LOG_DIR = os.environ.get("AZUREML_LOGDIRECTORY_PATH", os.getcwd())
        self.azureml_log_file_path = os.path.join(AZUREML_LOG_DIR, AZUREML_LOG_FILE_NAME)
        self.diag_log = diagnostic_log(self.azureml_log_file_path)

    def __enter__(self):
        self.diag_log.start_capture()

    def __exit__(self, exc_type, exc_value, tb):
        try:
            self.diag_log.stop_capture()
            has_azureml_log_file = os.path.exists(self.azureml_log_file_path)
            if has_azureml_log_file:
                self.run.upload_file(AZUREML_LOGS + "/" + AZUREML_LOG_FILE_NAME, self.azureml_log_file_path)
                open(self.azureml_log_file_path, 'r+').truncate(0)
        except Exception as e:
            pass
