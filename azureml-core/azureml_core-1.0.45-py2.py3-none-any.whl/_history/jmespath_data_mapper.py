# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import datetime
import pytz
import jmespath


class JmesPathDataMapper(object):
    RUN_ID = "run_id"
    RUN_NUMBER = 'run_number'
    SCRIPT_NAME = "script_name"
    EXPERIMENT_ID = "experiment_id"
    PARENT_EXPERIMENT_ID = "parent_run_id"
    NAME = "name"
    PATH = "path"
    DESCRIPTION = "description"
    CREATION_TIME = "created_utc"
    START_TIME = "start_time_utc"
    END_TIME = "end_time_utc"
    STATUS = "status"
    CELLS = 'cells'
    DURATION = 'duration'

    def map_runs(self, runs, metrics=None, status=None, query=None):
        """ Maps the runs data to tabular data that can be consumed by terminaltables
        Returns:
            tuple: tuples of run entries, including the caption row.
        """

        # Add a duration property
        for run in runs:
            start_time = run.get(self.START_TIME, None)
            stop_time = run.get(self.END_TIME, None)

            if run[self.STATUS] == "NotStarted" or run[self.STATUS] == "Running":
                stop_time = datetime.datetime.now(pytz.utc)

            if start_time and isinstance(start_time, str):
                start_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            if stop_time and isinstance(stop_time, str):
                stop_time = datetime.datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            duration = str(
                stop_time - start_time) if start_time and stop_time and stop_time > start_time else "N/A"
            # list is sorted by startd time. If a run is not started, set the time as 'not started'
            run[self.START_TIME] = start_time if start_time else '00:00 not started'
            run[self.DURATION] = duration

        # transfer datatime to string for output and jmes query
        self.transfer_datetime_to_string(runs)
        sort_filter = 'sort_by([*], &{0})[::-1]'.format(self.START_TIME)

        if query is not None:
            expression = self.get_pipe_expression([sort_filter, query])
        else:
            status_filter = self.get_status_expression(
                status) if status else None
            head_names = '{0}: {0}, {1}: {1}, {2}: {2}, {3}: {3}, {4}: {4}'.format(
                self.RUN_ID, self.SCRIPT_NAME, self.STATUS, self.START_TIME, self.DURATION)
            header_filter = '[*].{0}{1}{2}'.format('{', head_names, '}')
            filter_list = [sort_filter, status_filter,
                           header_filter] if status_filter else [sort_filter, header_filter]
            expression = self.get_pipe_expression(filter_list)

        results = jmespath.search(expression, runs)

        if metrics is not None and len(metrics) > 0:
            for run in results:
                run_id_expression = jmespath.compile(
                    JmesPathDataMapper.get_runid_expression(run.get(self.RUN_ID)))
                run_metrics = run_id_expression.search(metrics)
                if run_metrics is not None and len(run_metrics) > 0:
                    self._insert_metrics_to_run(run, run_metrics)

        return results

    def map_run(self, run, attachments, run_metrics):
        result = run
        self.transfer_datetime_to_string(result)
        if run_metrics is not None:
            self._insert_metrics_to_run(result, run_metrics)

        if attachments is not None:
            names = jmespath.search('[*].{0}'.format(self.PATH), attachments)

            # backward compatible if reference old version (<1.2.0) of azure.dmsclient
            if not names:
                names = jmespath.search(
                    '[*].{0}'.format(self.NAME), attachments)

            attachment_names = ', '.join(names)
            result['attachments'] = attachment_names

        return result

    def compare_runs(self, runs, metrics):
        result = []
        if len(runs) <= 1:
            return result

        self.transfer_datetime_to_string(runs)

        if metrics is not None:
            for run in runs:
                run_id_expression = jmespath.compile(
                    JmesPathDataMapper.get_runid_expression(run[self.RUN_ID]))
                run_metrics = run_id_expression.search(metrics)
                if run_metrics is not None:
                    self._insert_metrics_to_run(run, run_metrics)

        return runs

    @staticmethod
    def _insert_metrics_to_run(run, run_metrics):
        if run_metrics is not None and len(run_metrics) > 0:
            metrics_cells = {}
            for metric in run_metrics:
                for cell in metric.get(JmesPathDataMapper.CELLS):
                    if cell is not None:
                        metrics_cells = JmesPathDataMapper._merge_two_dictionary(
                            metrics_cells, cell)
            run.update(metrics_cells)

    @staticmethod
    def _merge_two_dictionary(dictionary_1, dictionary_2):
        result = {}
        result.update(dictionary_1)
        result.update(dictionary_2)

        # if merged value being override
        for key, value_dict1 in dictionary_1.items():
            if key in dictionary_2:
                value_dict2 = dictionary_2.get(key)
                tmp_merge = value_dict1 if isinstance(
                    value_dict1, list) else [value_dict1]

                if isinstance(value_dict2, list):
                    tmp_merge.extend(value_dict2)
                else:
                    tmp_merge.append(value_dict2)

                result[key] = tmp_merge

        return result

    @staticmethod
    def get_status_expression(status_id):
        if status_id is not None:
            status = status_id.lower()
            if status == 'completed':
                status = 'Completed'
            elif status == 'canceled':
                status = 'Canceled'
            elif status == 'failed':
                status = 'Failed'
            elif status == 'running':
                status = 'Running'
            elif status == 'notstarted':
                status = 'NotStarted'
            else:
                raise ValueError(
                    "Unsupported status value: {0}".format(status_id))
            return JmesPathDataMapper.get_filter_expression(JmesPathDataMapper.STATUS, '==', status)
        raise ValueError("Argument 'status_id' is null")

    @staticmethod
    def transfer_datetime_to_string(data):
        if data is None:
            return

        if isinstance(data, list):
            for row in data:
                JmesPathDataMapper.transfer_datetime_to_string(row)
            return

        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, datetime.datetime):
                    data[k] = v.isoformat()
            return

    @staticmethod
    def get_runid_expression(run_id):
        return JmesPathDataMapper.get_filter_expression(JmesPathDataMapper.RUN_ID, '==', str(run_id))

    @staticmethod
    def get_sortby_expression(key_name):
        return 'sort_by([*], &{0})'.format(key_name)

    @staticmethod
    def get_reverse_expression():
        return '[::-1]'

    @staticmethod
    def get_filter_expression(filter_name, comparator, value):
        return '[?{0}{1}`{2}`]'.format(filter_name, comparator, value)

    @staticmethod
    def get_pipe_expression(list_expression):
        return '|'.join(list_expression)
