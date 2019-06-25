# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import json
import math
import re

from azureml.widgets._constants import MULTIRUN_WIDGET_REFRESH_SLEEP_TIME, WIDGET_REFRESH_SLEEP_TIME_DATABRICKS
from azureml.widgets.run_details import PLATFORM
# noinspection PyProtectedMember
from azureml.widgets._userrun._run_details import _UserRunDetails
# noinspection PyProtectedMember
from azureml.widgets._hyperdrive._transformer import _HyperDriveDataTransformer


if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._hyperdrive._widget import _HyperDriveWidget
    REFRESH_SLEEP_TIME = MULTIRUN_WIDGET_REFRESH_SLEEP_TIME
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._hyperdrive._universal_widget import _HyperDriveWidget
    REFRESH_SLEEP_TIME = WIDGET_REFRESH_SLEEP_TIME_DATABRICKS


class _HyperDriveRunDetails(_UserRunDetails):
    """Hyperdrive run details widget."""

    def __init__(self, run_instance):
        """Initialize a HyperDrive widget call.

        :param run_instance: The hyperdrive run instance.
        :type run_instance: HyperDriveRun
        """
        super().__init__(run_instance, "HyperDrive", refresh_time=REFRESH_SLEEP_TIME,
                         widget=_HyperDriveWidget)

    def _update_children_with_metrics(self, child_runs, metrics):
        # for each child run add their corresponding best metric reached so far
        if metrics and metrics['series']:
            child_runs_local = copy.deepcopy(child_runs)

            pmc_goal = self._get_primary_config()['goal']
            pmc_name = self._get_primary_config()['name']
            func = max if pmc_goal == 'maximize' else min

            # check chart type. if there is 'run_id' in series that means each series corresponds to a run id
            # which corresponds to hyperdrive chart with line series, else it's scattered chart
            if metrics['series'][pmc_name] and 'run_id' in metrics['series'][pmc_name][0]:
                for series in metrics['series'][pmc_name]:
                    run = next(x for x in child_runs_local if x['run_number'] == series['run_id'])
                    if run:
                        run['best_metric'] = func(series['data'])
            else:
                goal_name = '_min' if pmc_goal == 'minimize' else '_max'
                primary_metric = {}
                best_metric = {}

                for _key, dataList in metrics['series'].items():
                    for x in dataList:
                        if x['name'] == pmc_name:
                            primary_metric = dict(zip(x['categories'], x['data']))
                        elif x['name'] == pmc_name + goal_name:
                            best_metric = dict(zip(x['categories'], x['data']))

                for num in range(0, len(child_runs_local)):
                    run_number = child_runs_local[num]['run_number']
                    child_runs_local[num]['metric'] = round(primary_metric[run_number], 8) \
                        if run_number in primary_metric \
                        and not math.isnan(float(primary_metric[run_number])) else None
                    child_runs_local[num]['best_metric'] = round(best_metric[run_number], 8) \
                        if run_number in best_metric \
                        and not math.isnan(float(best_metric[run_number])) else None

            return child_runs_local

    def _add_additional_properties(self, run_properties):
        super()._add_additional_properties(run_properties)

        tags = run_properties['tags']
        if 'generator_config' in tags:
            generator_config = json.loads(tags['generator_config'])
            run_properties['hyper_parameters'] = generator_config['parameter_space']
            hyperParams = run_properties['hyper_parameters']

            assert isinstance(hyperParams, dict) is True, "HyperParameters is not a dictionary"

    def _get_child_runs(self):
        _child_runs = super()._get_child_runs()
        prepRunSuccess = None
        for run in _child_runs:
            run_id = run['run_id']
            run_type = run['run_type']
            run_status = run['status']
            if(run_type == 'preparation' and run_status != 'Failed'):
                prepRunSuccess = run
                continue

            if run_id in self.tags:
                arguments = json.loads(self.tags[run_id])
                if arguments:
                    for name, value in arguments.items():
                        run['param_' + name] = value

        if prepRunSuccess is not None:
            _child_runs.remove(prepRunSuccess)

        return _child_runs

    def _post_process_log(self, log_name: str, log_content: str) -> str:
        # Hyperdrive currently has additional start and end tags with no line-break (due to a bug in artifact service
        # Below logic splits log content into lines based on these tags
        if "hyperdrive" in log_name:
            lines = re.findall(r'(?<=<START>)(.*?)(?=<END>)', log_content)
            if lines:
                log_content = '\r\n'.join(lines)
        return super()._post_process_log(log_name, log_content)

    def _get_primary_config(self):
        collection = self.properties if 'primary_metric_config' in self.properties else self.tags
        c = json.loads(collection['primary_metric_config'])
        config = {
            'name': c['name'],
            'goal': c['goal']
        }
        return config

    def _create_transformer(self):
        return _HyperDriveDataTransformer()
