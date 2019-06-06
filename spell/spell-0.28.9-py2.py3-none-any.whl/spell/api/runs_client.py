import json

from dateutil.parser import isoparse
from requests.exceptions import ChunkedEncodingError, ReadTimeout, ConnectionError

from spell.api import base_client
from spell.api.exceptions import ClientException, JsonDecodeError, WaitError
from spell.api.utils import url_path_join, to_RFC3339_string
from spell.api.models import ValueSpec, RangeSpec


RUNS_RESOURCE_URL = "runs"

LOGS_RESOURCE_URL = "logs"
LS_RESOURCE_URL = "ls"
KILL_RESOURCE_URL = "kill"
KILL_BATCH_RESOURCE_URL = "kill_batch"
STOP_RESOURCE_URL = "stop"
STOP_BATCH_RESOURCE_URL = "stop_batch"
COPY_RESOURCE_URL = "cp"
STATS_RESOURCE_URL = "stats"
WAIT_STATUS_RESOURCE_URL = "wait_status"
WAIT_METRIC_RESOURCE_URL = "wait_metric"
METRICS_RESOURCE_URL = "user-metrics"
HYPER_SEARCH_RESOURCE_URL = "hyper_search"

# Note(Brian):
# - connection timeout is slightly larger than a multiple of 3 as recommended
#   here: http://docs.python-requests.org/en/master/user/advanced/#timeouts
# - read timeout is set to 120 seconds to mitigate previous issues seen with stale
#   long-lived connections
CONN_TIMEOUT = 6.05
READ_TIMEOUT = 120


class RunsClient(base_client.BaseClient):

    def run(self, run_req):
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner), payload=run_req)
        self.check_and_raise(r)
        resp = self.get_json(r)
        run = resp["run"]
        if "already_existed" in resp and resp["already_existed"]:
            run.already_existed = True
        return run

    def hyper_grid_search(self, params, run_req):
        """Create a hyperparameter grid search

        Keyword arguments:
        params -- a dictionary mapping str -> models.ValueSpec
        run_req -- a RunRequest object

        Returns:
        a HyperSearch object

        """
        payload = {
            "grid_params": params,
            "run": run_req,
        }
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL),
                         payload=payload)
        self.check_and_raise(r)
        resp = self.get_json(r)
        hyper = resp["hyper_search"]
        return hyper

    def hyper_random_search(self, params, num_runs, run_req):
        """Create a hyperparameter random search

        Keyword arguments:
        params -- a dictionary mapping str -> models.ValueSpec or models.RangeSpec objects
        num_runs -- an int specifying the number of runs to create
        run_req -- a RunRequest object

        Returns:
        a HyperSearch object

        """
        param_payload = {}
        for k, v in params.items():
            if isinstance(v, ValueSpec):
                param_payload[k] = {"value_spec": v}
            elif isinstance(v, RangeSpec):
                param_payload[k] = {"range_spec": v}
            else:
                raise ClientException("values of params must be either a ValueSpec of RangeSpec")
        payload = {
            "num_runs": num_runs,
            "random_params": param_payload,
            "run": run_req,
        }
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL),
                         payload=payload)
        self.check_and_raise(r)
        resp = self.get_json(r)
        hyper = resp["hyper_search"]
        return hyper

    def hyper_bayesian_search(self, params, num_runs, parallel_runs, metric, metric_agg, run_req):
        """Create a hyperparameter bayesian search

        Keyword arguments:
        params -- a dictionary mapping str -> models.RangeSpec objects
        num_runs -- an int specifying the maximum number of runs to create
        parallel_runs -- an int specifying the number of runs to parallelize
        metric -- the metric used to evaluate runs
        metric_agg -- the aggregation method for the metric
        run_req -- a RunRequest object

        Returns:
        a HyperSearch object

        """
        param_payload = {}
        for k, v in params.items():
            if isinstance(v, RangeSpec):
                param_payload[k] = {"range_spec": v}
            else:
                raise ClientException("values of params must be a RangeSpec")
        payload = {
            "num_runs": num_runs,
            "parallel_runs": parallel_runs,
            "metric": metric,
            "metric_aggregation": metric_agg,
            "bayesian_params": params,
            "run": run_req,
        }
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL),
                         payload=payload)
        self.check_and_raise(r)
        resp = self.get_json(r)
        hyper = resp["hyper_search"]
        return hyper

    def get_hyper_search(self, hyper_search_id):
        """Get a hyperparameter search.

        Keyword arguments:
        hyper_search_id -- the id of the hyperparameter search

        Returns:
        a HyperSearch object
        """
        r = self.request("get", url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL,
                         hyper_search_id))
        self.check_and_raise(r)
        return self.get_json(r)["hyper_search"]

    def kill_hyper_search(self, hyper_search_id):
        """Kill a hyperparameter search.

        Keyword arguments:
        hyper_search_id -- the id of the hyperparameter search
        """
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL,
                         hyper_search_id, KILL_RESOURCE_URL))
        self.check_and_raise(r)

    def stop_hyper_search(self, hyper_search_id):
        """Stop a hyperparameter search.

        Keyword arguments:
        hyper_search_id -- the id of the hyperparameter search
        """
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL,
                         hyper_search_id, STOP_RESOURCE_URL))
        self.check_and_raise(r)

    def list_runs(self, workspace_ids=None, include_jupyter=False):
        """Get a list of runs.

        Keyword arguments:
        workspace_ids -- the ids of the workspaces to filter the runs by [OPTIONAL]
        include_jupyter -- include jupyter workspace runs

        Returns:
        a list of Run objects for this user

        """
        url = url_path_join(RUNS_RESOURCE_URL, self.owner)
        params = {}
        params["workspace_id"] = workspace_ids
        params["include_jupyter"] = include_jupyter
        r = self.request("get", url, params=params)
        self.check_and_raise(r)
        return self.get_json(r)["runs"]

    def get_run(self, run_id):
        """Get a run.

        Keyword arguments:
        run_id -- the id of the run

        Returns:
        a Run object
        """
        r = self.request("get", url_path_join(RUNS_RESOURCE_URL, self.owner, run_id))
        self.check_and_raise(r)
        return self.get_json(r)["run"]

    def get_run_log_entries(self, run_id, follow, offset):
        """Get log entries for a run.

        Keyword arguments:
        run_id -- the id of the run
        follow -- true if the logs should be followed
        offset -- which log line to start from

        Returns:
        a generator for entries of run logs
        """
        finished = False
        while not finished:
            if offset is None:
                raise ClientException("Missing log stream offset")
            payload = {"follow": follow, "offset": offset}
            with self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, run_id, LOGS_RESOURCE_URL),
                              payload=payload, stream=True, timeout=(CONN_TIMEOUT, READ_TIMEOUT)) as log_stream:
                self.check_and_raise(log_stream)
                try:
                    if log_stream.encoding is None:
                        log_stream.encoding = 'utf-8'
                    for chunk in log_stream.iter_lines(decode_unicode=True):
                        try:
                            chunk = json.loads(chunk, cls=base_client.SpellDecoder)
                        except ValueError as e:
                            message = "Error decoding the log response chunk: {}".format(e)
                            raise JsonDecodeError(msg=message, response=log_stream, exception=e)
                        offset = chunk.get("next_offset", offset)
                        logEntry = chunk.get("log_entry")
                        finished = chunk.get("finished")
                        if logEntry:
                            yield logEntry
                        elif finished:
                            break
                # TODO(Brian): remove ConnectionError once requests properly raises ReadTimeout
                except (ChunkedEncodingError, ReadTimeout, ConnectionError):
                    continue  # Try reconnecting

    def remove_run(self, run_id):
        """Soft delete a run, don't show in ps or ls.

        Keyword arguments:
        run_id -- the id of the run to remove

        Returns:
        nothing if successful
        """
        r = self.request("delete", url_path_join(RUNS_RESOURCE_URL, self.owner, str(run_id)))
        self.check_and_raise(r)

    def kill_run(self, run_id):
        """Kill a currently running run.

        Keyword arguments:
        run_id -- the id of the run
        """
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, run_id, KILL_RESOURCE_URL))
        self.check_and_raise(r)

    def kill_runs(self, run_ids):
        """Batch kill runs.

        Keyword arguments:
        run_ids -- a list of run_ids (integers) to kill

        Returns:
        a dictionary with the following keys:
            failed_run_ids: list of run_ids (integers) that could not be killed due to a server side error
            non_existent_run_ids: list of run_ids (integers) that were invalid
            final_state_run_ids: list of run_ids (integers) that were already finished when kill was called
            successful_run_ids: list of run_ids (integers) that were successfully killed
        """
        payload = {"run_ids": run_ids}
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, KILL_BATCH_RESOURCE_URL), payload=payload)
        self.check_and_raise(r)
        data = r.json()
        return data

    def stop_run(self, run_id):
        """Stop a currently running run.

        Keyword arguments:
        run_id -- the id of the run to stop
        """
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, run_id, STOP_RESOURCE_URL))
        self.check_and_raise(r)

    def stop_runs(self, run_ids):
        """Stop a set of currently running runs.

        Keyword arguments:
        run_id -- the id of the run to stop

        Returns:
        a dictionary with the following keys: 'failed_run_ids', 'non_existent_run_ids',
        'pre_running_run_ids', 'post_running_run_ids', 'successful_run_ids'
        """
        payload = {"run_ids": run_ids}
        r = self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, STOP_BATCH_RESOURCE_URL), payload=payload)
        self.check_and_raise(r)
        data = r.json()
        return data

    def get_stats(self, run_id, follow=False):
        """Get statistics for a run.

        Keyword arguments:
        run_id -- the id of the run

        Returns:
        a generator of (cpu_stats, gpu_stats) tuples for the run
        """
        finished = False
        while not finished:
            payload = {"follow": follow}
            with self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, run_id, STATS_RESOURCE_URL),
                              payload=payload, stream=True) as stats_stream:
                self.check_and_raise(stats_stream)
                try:
                    if stats_stream.encoding is None:
                        stats_stream.encoding = 'utf-8'
                    for chunk in stats_stream.iter_lines(decode_unicode=True):
                        try:
                            chunk = json.loads(chunk, cls=base_client.SpellDecoder)
                        except ValueError as e:
                            message = "Error decoding the stats response chunk: {}".format(e)
                            raise JsonDecodeError(msg=message, response=stats_stream, exception=e)
                        cpu_stats, gpu_stats = chunk.get("cpu_stats"), chunk.get("gpu_stats")
                        finished = chunk.get("finished")
                        if cpu_stats:
                            yield (cpu_stats, gpu_stats)
                        elif finished:
                            break
                except ChunkedEncodingError:
                    continue  # Try reconnecting

    def get_run_metrics(self, run_id, metric_name, follow=False, offset=None):
        """Get user metrics for a run

        Keyword arguments:
        run_id -- the id of the run
        metric_name -- the metric name
        follow -- true if metrics should be followed until the run is complete
        offset -- a datetime.datetime object specifying a time offset to start from.
            offset is exclusive (i.e., returned metrics will be > offset)

        Returns:
        a generator of metrics for the run
        """
        finished = False
        if offset:
            offset = to_RFC3339_string(offset)
        while not finished:
            payload = {"metrics": [{"name": metric_name, "offset": offset}], "follow": follow}
            with self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, run_id, METRICS_RESOURCE_URL),
                              payload=payload, stream=True) as metric_stream:
                self.check_and_raise(metric_stream)
                if metric_stream.encoding is None:
                    metric_stream.encoding = 'utf-8'
                try:
                    for chunk in metric_stream.iter_lines(decode_unicode=True):
                        chunk = json.loads(chunk)
                        if chunk.get("connected"):
                            # initial connection chunk of long-lived response
                            continue
                        metrics = chunk.get("metrics_by_name")
                        if metrics:
                            for metric in metrics[metric_name]["data"]:
                                offset = metric[0]
                                timestamp = isoparse(metric[0])
                                index = metric[1]
                                value = metric[2]
                                yield (timestamp, index, value)
                        finished = chunk.get("finished") or not metric_stream.headers.get("stream")
                        if finished:
                            break
                except ChunkedEncodingError:
                    continue  # Try reconnecting
                except ValueError as e:
                    message = "Error decoding the metric response chunk: {}".format(e)
                    raise JsonDecodeError(msg=message, response=metric_stream, exception=e)

    def wait_status(self, run_id, *statuses):
        """Wait for a run to reach a given status.

        Keyword arguments:
        run_id -- the id of the run to wait on
        statuses -- variable length list of status to wait for. Allowed values: "building", "running", "saving",
            "pushing", "complete", "failed", "killed", "stopped"
        """
        payload = {"statuses": statuses}
        finished = False
        while not finished:
            with self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, run_id, WAIT_STATUS_RESOURCE_URL),
                              payload=payload, stream=True, timeout=(CONN_TIMEOUT, READ_TIMEOUT)) as status_stream:
                self.check_and_raise(status_stream)
                try:
                    if status_stream.encoding is None:
                        status_stream.encoding = 'utf-8'
                    for chunk in status_stream.iter_lines(decode_unicode=True):
                        try:
                            chunk = json.loads(chunk)
                        except ValueError as e:
                            message = "Error decoding the wait status response: {}".format(e)
                            raise JsonDecodeError(msg=message, response=status_stream, exception=e)
                        if chunk.get("success") is None:
                            # this is initial connection message
                            continue
                        finished = True
                        if chunk.get("success"):
                            return
                        else:
                            raise WaitError(msg=chunk.get("error"), response=status_stream)
                # TODO(Brian): remove ConnectionError once requests properly raises ReadTimeout
                except (ChunkedEncodingError, ReadTimeout, ConnectionError):
                    continue  # Try reconnecting

    def wait_metric(self, run_id, metric_name, condition, value):
        """Wait for a run metric to reach a given condition.

        Keyword arguments:
        run_id -- the id of the run to wait on
        metric_name -- the name of the metric to wait on
        condition -- condition to wait for. Allowed values: "eq", "gt", "gte", "lt", "lte"
        value -- the value to evaluate the condition against
        """
        payload = {"metric_name": metric_name, "condition": condition, "value": value}
        finished = False
        while not finished:
            with self.request("post", url_path_join(RUNS_RESOURCE_URL, self.owner, run_id, WAIT_METRIC_RESOURCE_URL),
                              payload=payload, stream=True, timeout=(CONN_TIMEOUT, READ_TIMEOUT)) as metric_stream:
                self.check_and_raise(metric_stream)
                try:
                    if metric_stream.encoding is None:
                        metric_stream.encoding = 'utf-8'
                    for chunk in metric_stream.iter_lines(decode_unicode=True):
                        try:
                            chunk = json.loads(chunk)
                        except ValueError as e:
                            message = "Error decoding the wait metric response: {}".format(e)
                            raise JsonDecodeError(msg=message, response=metric_stream, exception=e)
                        if chunk.get("success") is None:
                            # this is initial connection message
                            continue
                        finished = True
                        if chunk.get("success"):
                            return
                        else:
                            raise WaitError(msg=chunk.get("error"), response=metric_stream)
                # TODO(Brian): remove ConnectionError once requests properly raises ReadTimeout
                except (ChunkedEncodingError, ReadTimeout, ConnectionError):
                    continue  # Try reconnecting
