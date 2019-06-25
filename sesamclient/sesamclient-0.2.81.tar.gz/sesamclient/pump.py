# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import pprint
import textwrap
import time
import copy
import dateutil.parser

from .entitybase import EntityBase
from .exceptions import PumpIsAlreadyRunning, TimeoutWhileWaitingForRunningPumpToFinishException, \
    PumpDoesNotSupportTheOperation
from .utils import validate_response_is_ok


def parse_datetime(datetimestring):
    if not datetimestring:
        return None
    return dateutil.parser.parse(datetimestring)


class Pump(EntityBase):
    """
    """

    def __init__(self, pipe, connection, raw_jsondata):
        self.pipe = pipe
        self.pipe_id = pipe.id
        super().__init__(connection, raw_jsondata)

    @property
    def id(self):
        return "pump:" + self.pipe_id

    @property
    def type(self):
        return "pump"

    @property
    def runtime(self):
        return copy.deepcopy(self._raw_jsondata["runtime"])

    def __str__(self):
        result = super().__str__()
        result += "\n    pipe_id:%r" % (self.pipe_id,)
        return result

    def get_is_running(self):
        # Note: we must retrieve up-to-date information from the server, since the runtime stuff is so
        #       dynamic.
        self.update_raw_jsondata_from_url(self._connection.get_pipe_pump_url(self.pipe_id))
        return self._raw_jsondata["runtime"]["is-running"]

    def update_raw_jsondata(self, new_raw_jsondata):
        super().update_raw_jsondata(new_raw_jsondata)

        # Patch up the _raw_jsondata on the pipe, as well.
        # noinspection PyProtectedMember
        if "runtime" in self._raw_jsondata:
            self.pipe._raw_jsondata["runtime"].update(self._raw_jsondata["runtime"])

    def wait_for_pump_to_finish_running(self, timeout=60, poll_interval=0.5, verbosity=0):
        """Utility method for waiting until the pump is no longer running. This is useful in
        integration tests that want to make sure that the pump has been run after the test-code has
        modified the data in the source-system of a pipe.

        :param timeout: The maximum time to wait for the pump to stop running. If the timeout is exceeded,
                        an error is raised.
        """
        starttime = time.monotonic()
        time_of_last_log_output = 0
        while True:
            if not self.get_is_running():
                # ok, we are not running, so we can exit now.
                break

            elapsedtime = time.monotonic() - starttime
            if elapsedtime > timeout:
                raise TimeoutWhileWaitingForRunningPumpToFinishException(
                    "Timed out while waiting for the pump to finish running! pump:\n%s" % (
                        self.as_json(),))

            if verbosity > 0:
                current_time = time.monotonic()
                if (time.monotonic() - time_of_last_log_output) > 3:
                    if verbosity > 1:
                        print("Waiting for the pipe '%s' to finish running (elapsed time: %.2fs). "
                              "Progress:\n%s\n  Last-seen:%s" % (
                                  self.id,
                                  elapsedtime,
                                  textwrap.indent(pprint.pformat(self.runtime["progress"]), prefix="    "),
                                  self.runtime["last-seen"],
                              ))
                    else:
                        print("Waiting for the pipe '%s' to finish running (elapsed time: %.2fs). "
                              "Processed:%s  Last-seen:%s" % (
                                  self.id,
                                  elapsedtime,
                                  self.runtime["progress"]["processed"],
                                  self.runtime["last-seen"],
                              ))
                    time_of_last_log_output = current_time

            time.sleep(poll_interval)

    def has_pending_work(self):
        """Utility method for checking that the pumps source-queue and dependency-queue are empty. If the
        queues are empty, the pump will not produce any output if it is run.
        This is useful in integration tests that want to make sure that all indexing, etc that the pump
        depends on has been done, so that the pump output has reached its "eventually consistent" state.
        """
        if self.get_is_running():
            # The pump is running, so clearly it has pending work
            return True

        # Note: the get_is_running() method will have retrieved up-to-date information from the server,
        #       so we don't have to do it here.
        queues = self._raw_jsondata["runtime"]["queues"]

        def has_pending_work(dict_or_integer):
            if dict_or_integer is None:
                return False

            if isinstance(dict_or_integer, dict):
                for dataset_id, queue_size in dict_or_integer.items():
                    if queue_size is not None and queue_size > 0:
                        return True
            else:
                if dict_or_integer > 0:
                    return True
            return False

        if has_pending_work(queues.get("dependencies")):
            return True

        if has_pending_work(queues.get("source")):
            return True

        return False

    def run_pump_until_there_are_no_pending_work(self, timeout=60, sleep_time_between_runs=0.5, verbosity=0):
        """Utility method for running the pump until the has_pending_work() method return False.

        :param timeout: The maximum time to wait for the pump to finish. If the timeout is exceeded,
                        an error is raised.
        :sleep_time_between_runs: How long to sleep before restarting the pipe when the has_pending_work() method
                                  has returned True.

        """
        self.wait_for_pump_to_finish_running(timeout=timeout, verbosity=verbosity)
        self.start()
        self.wait_for_pump_to_finish_running(timeout=timeout, verbosity=verbosity)

        starttime = time.monotonic()
        while True:
            if not self.has_pending_work():
                # Ok, we are done.
                return

            elapsedtime = time.monotonic() - starttime
            if elapsedtime > timeout:
                raise TimeoutWhileWaitingForRunningPumpToFinishException(
                    "Timed out while waiting for the '%s' pump to complete all its pending work! pump:\n%s" % (
                        self.pipe_id, self.as_json(),))
            time.sleep(sleep_time_between_runs)

            self.wait_for_pump_to_finish_running(timeout=timeout, verbosity=verbosity)
            self.start()
            self.wait_for_pump_to_finish_running(timeout=timeout, verbosity=verbosity)

    @property
    def last_message(self):
        return self._raw_jsondata["runtime"]["last-message"]

    @property
    def last_original_error_message(self):
        return self._raw_jsondata["runtime"].get("last-original-error-message")

    @property
    def last_seen(self):
        return self._raw_jsondata["runtime"]["last-seen"]

    def reset_tracking(self):
        self.run_operation("reset-tracking", allowable_response_status_codes=frozenset([200]))

    def set_tracking_to_start(self):
        self.run_operation("set-tracking-to-start", allowable_response_status_codes=frozenset([200]))

    def unset_last_seen(self):
        self.update_last_seen("")

    def set_last_seen_to_end(self):
        self.run_operation("set-last-seen-to-end", allowable_response_status_codes=frozenset([200]))

    def update_last_seen(self, last_seen):
        last_seen = str(last_seen)
        self.run_operation("update-last-seen", operation_parameters={"last-seen": last_seen},
                           allowable_response_status_codes=frozenset([200]))

        # Check that the "last-seen"-attribute has been updated
        actual_last_seen = self.last_seen
        if actual_last_seen != last_seen:
            if (last_seen is None and actual_last_seen == "") or (last_seen == "" and actual_last_seen is None):
                # None and an empty string means the same here.
                pass
            else:
                raise AssertionError(
                    "Failed to update the 'last-seen'-value of the pump '%s'! expected value: '%s'  actual value: '%s'" % (
                        self.id, last_seen, actual_last_seen))

    @property
    def is_disabled(self):
        return self._raw_jsondata["runtime"]["is-disabled"]

    @property
    def is_valid_config(self):
        return self._raw_jsondata["runtime"]["is-valid-config"]

    @property
    def config_errors(self):
        return self._raw_jsondata["runtime"]["config-errors"]

    @property
    def last_run(self):
        return parse_datetime(self._raw_jsondata["runtime"]["last-run"])

    @property
    def next_run(self):
        return parse_datetime(self._raw_jsondata["runtime"]["next-run"])

    def disable(self):
        """Disable this pump. This prevents the pump from being automatically run by the task scheduler"""
        self._set_disabled_state(True)

    def enable(self):
        """Enable this pump."""
        self._set_disabled_state(False)

    def _set_disabled_state(self, is_disabled):
        # Send a put-request to disable the pump
        if self.is_disabled != is_disabled:
            if is_disabled:
                operation = "disable"
            else:
                operation = "enable"

            self.run_operation(operation, allowable_response_status_codes=frozenset([200]))

            # Check that the "is-disabled"-attribute has been updated
            actual_is_disabled = self.is_disabled
            if actual_is_disabled != is_disabled:
                raise AssertionError(("Failed to update the 'is-disabled' setting on the pump '"
                                      "'%s'! Expected value: '%s'  Actual value: '%s'") % (self.id, is_disabled,
                                                                                           actual_is_disabled))

    def start(self, dont_wait_for_pump_to_start=False, allow_already_running_pump=True, operation_parameters={}):
        """
        Starts the pump.

        :param dont_wait_for_pump_to_start: If this flag is set to True, the method will return without waiting for the
                                           pump to start running.
        :param allow_already_running_pump: If this  flag is set to False, this method will fail with a
                                           "PumpIsAlreadyRunning"-exception if if the pump was already
                                           running.
        """
        if dont_wait_for_pump_to_start:
            operation_parameters["dont-wait-for-pump-to-start"] = "true"

        response = self.run_operation("start", operation_parameters=operation_parameters,
                                      allowable_response_status_codes=frozenset([200, 409]))

        if response.status_code == 409:
            self.update_raw_jsondata(response.text)
            if allow_already_running_pump:
                return False
            else:
                raise PumpIsAlreadyRunning(self)

        validate_response_is_ok(response, 200)
        self.update_raw_jsondata(response.text)
        return True

    def stop(self):
        """
        Stops the pump.
        """
        self.run_operation("stop")

    @property
    def supported_operations(self):
        return self._raw_jsondata["runtime"]["supported-operations"]

    def run_operation(self,
                      operation,
                      operation_parameters=None,
                      allowable_response_status_codes=frozenset([200])):
        """Runs the specified operation on the pump.
        :param operation: The operation to run.
                          Must be one of the values of the :py:meth:`supported_operations` property.
        :param operation_parameters: A dict with operation parameters.
        :param allowable_response_status_codes: The http request status code(s) to accept (defaults to 200).
        """
        url = self._connection.get_pipe_pump_url(self.pipe_id)
        postdata = {"operation": operation}
        if operation_parameters is not None:
            postdata.update(operation_parameters)

        response = self._connection.do_post_request(url, data=postdata)

        # Handle the "operation not supported" 400 response, unless we have been told that 400-responses is
        # ok (in which case it is the callers responsibility to handle the error).
        if response.status_code == 400 and 400 not in allowable_response_status_codes:
            # check if this was caused by the pump not supporting the requested operation
            #
            if (
                    "doesn&#x27;t support the operation" in response.text or  # html response
                    "doesn't support the operation" in response.text):  # json response
                raise PumpDoesNotSupportTheOperation(pump=self,
                                                     operation=operation,
                                                     response=response)

        validate_response_is_ok(response, allowable_response_status_codes=allowable_response_status_codes)
        self.update_raw_jsondata(response.text)
        return response
