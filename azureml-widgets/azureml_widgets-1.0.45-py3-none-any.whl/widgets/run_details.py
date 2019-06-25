# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common widget implementations shared between various platforms."""
import importlib

from azureml.widgets._telemetry_logger import _TelemetryLogger

from . import _platform

# Jupyter Notebook
if _platform._in_jupyter_nb() is True:
    PLATFORM = 'JUPYTER'
# Databricks and others
else:
    PLATFORM = 'DATABRICKS'

logger = _TelemetryLogger.get_telemetry_logger(__name__)


def _create_rundetails_importer(run_type, class_name):
    def _soft_import_impl():
        mod_name = "azureml.widgets._{}._run_details".format(run_type)
        mod = importlib.import_module(mod_name)
        assert mod
        class_ref = getattr(mod, class_name)
        assert class_ref
        return class_ref
    return _soft_import_impl


class RunDetails:
    """
    Widget used for Training SDK run status.

    :param run_instance: Run instance for which the widget will be rendered.
    :type run_instance: azureml.core.run.Run
    """

    def __new__(cls, run_instance):
        """
        Return corresponding run details widget based on run type.

        :param run_instance: Run instance for which the widget will be rendered.
        :rtype azureml.widgets._widget_run_details_base._WidgetRunDetailsBase
        """
        _run_source_prop = 'azureml.runsource'
        widget_mapper = {
            'hyperdrive': _create_rundetails_importer("hyperdrive", "_HyperDriveRunDetails"),
            'automl': _create_rundetails_importer("automl", "_AutoMLRunDetails"),
            'azureml.PipelineRun': _create_rundetails_importer("pipeline", "_PipelineRunDetails"),
            'azureml.StepRun': _create_rundetails_importer("pipeline", "_StepRunDetails"),
            'experiment': None,
            'azureml.scriptrun': None
        }
        if run_instance.type is None:
            properties = run_instance.get_properties()
            if _run_source_prop in properties:
                run_type = properties[_run_source_prop].lower()
            else:
                run_type = 'experiment'
        else:
            run_type = run_instance.type

        widget_importer = widget_mapper.get(run_type)

        # If no importer is given for the presented type, default to _UserRunDetails
        if widget_importer is not None:
            class_ref = widget_importer()
            assert class_ref
            return class_ref(run_instance)
        else:
            # noinspection PyProtectedMember
            from azureml.widgets._userrun._run_details import _UserRunDetails
            return _UserRunDetails(run_instance)

    def __init__(self, run_instance):
        """
        Initialize widget with provided run instance.

        :param run_instance: Run instance for which the widget will be rendered.
        :type run_instance: azureml.core.run.Run
        """
        pass

    def show(self, render_lib=None, widget_settings=None):
        """
        Render widget and start thread to refresh the widget.

        :param render_lib: The library to use for rendering. Required only for databricks with value displayHTML
        :type render_lib: func
        :param widget_settings: Settings to be applied to widget. Supported settings are: 'debug' (boolean) and
                                'display' (str, Supported values: 'popup': to show widget in a pop-up).
        :type widget_settings: dict
        """
        pass

    def get_widget_data(self, widget_settings=None):
        """
        Retrieve and transform data from run history to be rendered by widget. Used also for debugging purposes.

        :param widget_settings: Settings to be applied to widget. Supported settings are: 'debug' (boolean) and
                                'display' (str, Supported values: 'popup': to show widget in a pop-up).
        :type widget_settings: dict
        :return: Dictionary containing data to be rendered by the widget.
        :rtype: dict
        """
        pass
