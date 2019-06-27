# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import json
import math

from azureml.widgets.run_details import PLATFORM
# noinspection PyProtectedMember
from azureml.widgets._userrun._run_details import _UserRunDetails
# noinspection PyProtectedMember
from azureml.widgets._automl._transformer import _AutoMLDataTransformer
# noinspection PyProtectedMember
from azureml.widgets._constants import AUTOML_WIDGET_REFRESH_SLEEP_TIME, WIDGET_REFRESH_SLEEP_TIME_DATABRICKS


if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._automl._widget import _AutoMLWidget
    REFRESH_SLEEP_TIME = AUTOML_WIDGET_REFRESH_SLEEP_TIME
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._automl._universal_widget import _AutoMLWidget
    REFRESH_SLEEP_TIME = WIDGET_REFRESH_SLEEP_TIME_DATABRICKS


class _AutoMLRunDetails(_UserRunDetails):
    """AutoML run details widget."""

    def __init__(self, run_instance):
        """Initialize a Run Details widget call.

        :param run_instance: automl run instance.
        :type run_instance: AutoMLRun
        """
        super().__init__(run_instance, "automl", refresh_time=REFRESH_SLEEP_TIME,
                         widget=_AutoMLWidget)

    def _update_children_with_metrics(self, child_runs, metrics):
        # for each child run add their corresponding primary metric values amd best metric reached so far
        if metrics and metrics['series']:
            child_runs_local = copy.deepcopy(child_runs)

            pmc = self._get_primary_config()['name']
            pmc_goal = self._get_primary_config()['goal']
            goal_name = '_min' if pmc_goal == 'minimize' else '_max'
            primary_metric = {}
            best_metric = {}

            for _key, dataList in metrics['series'].items():
                for x in dataList:
                    if x['name'] == pmc:
                        primary_metric = dict(zip(x['categories'], x['data']))
                    elif x['name'] == pmc + goal_name:
                        best_metric = dict(zip(x['categories'], x['data']))

            for num in range(0, len(child_runs_local)):
                iteration = child_runs_local[num]['iteration']
                if iteration in primary_metric:
                    child_runs_local[num]['primary_metric'] = round(primary_metric[iteration], 8) \
                        if iteration in primary_metric \
                        and not math.isnan(float(primary_metric[iteration])) else None
                    child_runs_local[num]['best_metric'] = round(best_metric[iteration], 8) \
                        if iteration in best_metric \
                        and not math.isnan(float(best_metric[iteration])) else None

            return child_runs_local

    def _get_mapped_metrics(self, metrics, child_runs):
        run_number_mapper = {c['run_id']: c['iteration'] for c in child_runs}
        return {run_number_mapper[k]: v for k, v in metrics.items()}

    def _get_metrics(self, child_runs):
        metrics = super()._get_metrics(child_runs)

        pmc = self._get_primary_config()['name']
        goal_name = '_min' if self._get_primary_config()['goal'] == 'minimize' else '_max'

        # Automl currently populates the max field; remove that to resolve conflict
        for run_id in metrics:
            metrics[run_id].pop(pmc + goal_name, None)

        return metrics

    def _get_primary_config(self):
        config_settings = json.loads(self.properties['AMLSettingsJsonString'])
        config = {
            'name': config_settings['primary_metric'],
            'goal': config_settings['metric_operation']
        }
        return config

    def _create_transformer(self):
        return _AutoMLDataTransformer()
