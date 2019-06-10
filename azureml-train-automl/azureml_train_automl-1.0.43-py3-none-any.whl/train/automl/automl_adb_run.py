# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
The automated machine learning ADB Run class.

This acts as a wrapper class around the AutoMLRun class and provides ADB specific implementations of certain methods.
"""
from azureml._restclient.constants import AUTOML_RUN_USER_AGENT
from .run import AutoMLRun


class AutoMLADBRun(AutoMLRun):
    """
    AutoMLADBRun inherits from AutoMLRun and holds specific properties related to ADB (Azure Databricks) execution.

    :param experiment: The experiment associated to the run.
    :type experiement: azureml.core.Experiment
    :param run_id: The id associated to the run.
    :type run_id: str
    :param adb_thread: Thread executing experiment on ADB.
    :type adb_thread: azureml.train.automl._AdbDriverNode
    """

    def __init__(self, experiment, run_id, adb_thread, **kwargs):
        """
        Initialize AutoMLADBRun.

        :param experiment: The experiment associated to the run.
        :type experiement: azureml.core.Experiment
        :param run_id: The id associated to the run.
        :type run_id: str
        :param adb_thread: Thread executing experiment on ADB.
        :type adb_thread: azureml.train.automl._AdbDriverNode
        """
        user_agent = kwargs.pop('_user_agent', AUTOML_RUN_USER_AGENT)
        super(AutoMLADBRun, self).__init__(experiment=experiment,
                                           run_id=run_id, _user_agent=user_agent, **kwargs)
        if adb_thread is None:
            raise Exception("adb_thread cannot be None")

        self.adb_thread = adb_thread

    def cancel(self):
        """
        Cancel an AutoML run.

        Return True if the AutoML run is canceled successfully.

        :return: None
        """
        super(AutoMLADBRun, self).cancel()

        try:
            self.adb_thread.cancel()
        except Exception as e:
            self._log_traceback(e)
            raise Exception("Failed while cancelling spark job with id: {}".format(
                self._run_id)) from None
        return True
