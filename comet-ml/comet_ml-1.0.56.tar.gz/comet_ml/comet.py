# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
Author: Gideon Mendels

This module contains the main components of comet.ml client side

"""
from __future__ import print_function

import json
import logging
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import uuid
from math import isnan
from os.path import basename

from comet_ml._logging import STREAMER_WAIT_FOR_FINISH_FAILED
from comet_ml._reporting import ON_EXIT_DIDNT_FINISH_UPLOAD_SDK
from comet_ml.config import (
    ADDITIONAL_STREAMER_UPLOAD_TIMEOUT,
    DEFAULT_STREAMER_MSG_TIMEOUT,
)
from comet_ml.connection import format_messages_for_ws
from comet_ml.file_uploader import upload_file_thread
from comet_ml.json_encoder import NestedEncoder
from comet_ml.utils import local_timestamp, wait_for_empty
from six.moves.queue import Empty, Queue
from six.moves.urllib.parse import urlencode, urlsplit, urlunsplit

DEBUG = False
ENV_OPTIMIZATION_ID = "COMETML_OPTIMIZATION_ID_{api_key}"
LOGGER = logging.getLogger(__name__)


class CloseMessage(object):
    """ A special messag indicating Streamer to ends and exit
    """

    pass


class BaseStreamer(threading.Thread):
    def __init__(self, initial_offset, queue_timeout):
        threading.Thread.__init__(self)

        self.counter = initial_offset
        self.messages = Queue()
        self.queue_timeout = queue_timeout

        LOGGER.debug("%r instantiated with duration %s", self, self.queue_timeout)

    def put_messge_in_q(self, message):
        """
        Puts a message in the queue
        :param message: Some kind of payload, type agnostic
        """
        if message is not None:
            LOGGER.debug("Putting 1 %r in queue", message.__class__)
            self.messages.put(message)

    def _before_run(self):
        pass

    def run(self):
        """
        Continuously pulls messages from the queue and process them.
        """
        self._before_run()

        while True:
            out = self._loop()

            # Exit the infinite loop
            if isinstance(out, CloseMessage):
                break

        self._after_run()

        LOGGER.debug("%s has finished", self.__class__)

        return

    def _after_run(self):
        pass

    def getn(self, n):
        """
        Pops n messages from the queue.
        Args:
            n: Number of messages to pull from queue

        Returns: n messages

        """
        try:
            msg = self.messages.get(
                timeout=self.queue_timeout
            )  # block until at least 1
        except Empty:
            LOGGER.debug("No message in queue, timeout")
            return None

        if isinstance(msg, CloseMessage):
            return [msg]

        self.counter += 1
        msg.set_offset(self.counter)
        result = [msg]
        try:
            while len(result) < n:
                another_msg = self.messages.get(
                    block=False
                )  # dont block if no more messages
                self.counter += 1
                another_msg.set_offset(self.counter)
                result.append(another_msg)
        except Exception:
            LOGGER.debug("Exception while getting more than 1 message", exc_info=True)
        return result


class Streamer(BaseStreamer):
    """
    This class extends threading.Thread and provides a simple concurrent queue
    and an async service that pulls data from the queue and sends it to the server.
    """

    def __init__(
        self,
        ws_connection,
        beat_duration,
        connection,
        initial_offset,
        experiment_key,
        api_key,
        run_id,
        project_id,
        optimization_id=None,
        pending_rpcs_callback=None,
        msg_waiting_timeout=DEFAULT_STREAMER_MSG_TIMEOUT,
        file_upload_timeout=ADDITIONAL_STREAMER_UPLOAD_TIMEOUT,
    ):
        super(Streamer, self).__init__(initial_offset, beat_duration / 1000.0)
        self.daemon = True
        self.name = "Streamer(%r)" % (ws_connection)
        self.ws_connection = ws_connection
        self.closed = False
        self.stop_processing = False
        self.last_beat = time.time()
        self.connection = connection
        self.msg_waiting_timeout = msg_waiting_timeout
        self.file_upload_timeout = file_upload_timeout

        self.on_gpu_monitor_interval = None

        self.on_pending_rpcs_callback = pending_rpcs_callback

        self.upload_threads = []

        self.experiment_key = experiment_key
        self.api_key = api_key
        self.run_id = run_id
        self.project_id = project_id
        self.optimization_id = optimization_id

        LOGGER.debug("Streamer instantiated with ws url %s", self.ws_connection)

    def close(self):
        """
        Puts a None in the queue which leads to closing it.
        """
        if self.closed is True:
            LOGGER.debug("Streamer tried to be closed more than once")
            return

        # Send a message to close
        self.put_messge_in_q(CloseMessage())

        self.closed = True

    def _before_run(self):
        self.ws_connection.wait_for_connection()

    def _loop(self):
        """
        A single loop of running
        """
        try:
            # If we should stop processing the queue, abort early
            if self.stop_processing is True:
                return CloseMessage()

            if self.ws_connection is not None and self.ws_connection.is_connected():
                messages = self.getn(1)

                if messages is not None:
                    LOGGER.debug(
                        "Got %d messages, %d still in queue",
                        len(messages),
                        self.messages.qsize(),
                    )
                    # TODO better group multiple WS messages
                    for message in messages:
                        if isinstance(message, CloseMessage):
                            return message
                        elif isinstance(message, UploadFileMessage):
                            self._process_upload_message(message)
                        elif isinstance(message, Message):
                            self._process_ws_message(message)

                try:
                    self._check_heartbeat()
                except Exception:
                    LOGGER.debug("Heartbeat error", exc_info=True)
            else:
                LOGGER.debug("WS connection not ready")
                # Basic backoff
                time.sleep(0.5)
        except Exception:
            LOGGER.debug("Unknown streaming error", exc_info=True)

    def _process_upload_message(self, message):
        # Compute the url from the upload type
        url = self.connection.get_upload_url(message.upload_type)

        upload_thread = upload_file_thread(
            project_id=self.project_id,
            experiment_id=self.experiment_key,
            file_path=message.file_path,
            upload_endpoint=url,
            api_key=self.api_key,
            additional_params=message.additional_params,
            clean=message.clean,
        )
        self.upload_threads.append(upload_thread)
        LOGGER.debug("Processing uploading message done")
        LOGGER.debug("Upload threads %s", self.upload_threads)

    def _process_ws_message(self, message):
        try:
            message_dict = message.repr_json()

            # Inject online specific values
            message_dict["apiKey"] = self.api_key
            message_dict["runId"] = self.run_id
            message_dict["projectId"] = self.project_id
            message_dict["optimization_id"] = self.optimization_id
            message_dict["experimentKey"] = self.experiment_key

            data = format_messages_for_ws([message_dict])
            self.ws_connection.send(data)
        except Exception:
            LOGGER.debug("WS sending error", exc_info=True)

    def _check_heartbeat(self):
        """
        Check if we should send an heartbeat
        """
        next_beat = self.last_beat + self.queue_timeout
        now = time.time()
        if next_beat < now:
            LOGGER.debug("Doing an hearbeat")
            # We need to udpate the last beat time before doing the actual
            # call as the call might fails and the last beat would not been
            # updated. That would trigger a heartbeat for each message.
            self.last_beat = time.time()
            new_beat_duration, gpu_monitor_interval, pending_rpcs = (
                self.connection.heartbeat()
            )
            LOGGER.debug("Getting a new heartbeat duration %d", new_beat_duration)
            LOGGER.debug(
                "Getting a new gpu monitor duration %d %r",
                gpu_monitor_interval,
                self.on_gpu_monitor_interval,
            )
            self.queue_timeout = new_beat_duration / 1000.0  # We get milliseconds

            # If we get a callback for the gpu_monitor duration, call it with
            # the new gpu monitor duration
            if self.on_gpu_monitor_interval is not None:
                try:
                    self.on_gpu_monitor_interval(gpu_monitor_interval / 1000.0)
                except Exception:
                    LOGGER.debug(
                        "Error calling the gpu monitor interval callback", exc_info=True
                    )

            # If there are some pending rpcs
            if pending_rpcs and self.on_pending_rpcs_callback is not None:
                try:
                    self.on_pending_rpcs_callback()
                except Exception:
                    LOGGER.debug("Error calling the rpc calback", exc_info=True)

    def wait_for_finish(self):
        """ Blocks the experiment from exiting until all data was sent to server OR 2 minutes passed."""

        msg = "Uploading stats to Comet before program termination (may take several seconds)"
        if not self._is_msg_queue_empty():
            LOGGER.info(msg)

            wait_for_empty(
                self._is_msg_queue_empty,
                self.msg_waiting_timeout,
                verbose=True,
                sleep_time=5,
            )

        if not self._is_msg_queue_empty():
            msg = "Failed to send all messages, metrics and output will likely be incomplete"
            LOGGER.warning(msg)

        # From now on, stop processing the message queue as it might contains file upload messages
        # TODO: Find a correct way of testing it
        self.stop_processing = True

        if not self._is_file_upload_done():
            msg = (
                "Waiting for completion of the file uploads (may take several seconds)"
            )
            LOGGER.info(msg)
            wait_for_empty(
                self._is_file_upload_done,
                self.file_upload_timeout,
                verbose=True,
                sleep_time=5,
            )

        if not self._is_msg_queue_empty() or not self._is_file_upload_done():
            remaining = self.messages.qsize()
            remaining_upload = len(
                [thread for thread in self.upload_threads if thread.is_alive() is True]
            )
            LOGGER.error(STREAMER_WAIT_FOR_FINISH_FAILED, remaining, remaining_upload)

            self.connection.report(
                event_name=ON_EXIT_DIDNT_FINISH_UPLOAD_SDK,
                err_msg=(
                    STREAMER_WAIT_FOR_FINISH_FAILED % (remaining, remaining_upload)
                ),
            )
            return False

        return True

    def _is_msg_queue_empty(self):
        finished = self.messages.empty()

        if finished is False:
            LOGGER.debug("Message queue not empty")

        return finished

    def _is_file_upload_done(self):
        finished = True

        for thread in self.upload_threads:
            thread_finished = thread.is_alive() is False
            finished = finished and thread_finished

        return finished


def compact_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), cls=NestedEncoder)


class OfflineStreamer(BaseStreamer):
    """
    This class extends threading.Thread and provides a simple concurrent queue
    and an async service that pulls data from the queue and sends it to the server.
    """

    def __init__(self, tmp_dir, initial_offset):
        super(OfflineStreamer, self).__init__(initial_offset, 1)
        self.daemon = True
        self.closed = False
        self.tmp_dir = tmp_dir

        self.file = open(os.path.join(self.tmp_dir, "messages.json"), "w")

    def close(self):
        """
        Puts a None in the queue which leads to closing it.
        """
        if self.closed is True:
            LOGGER.debug("Streamer tried to be closed more than once")
            return

        # Send a message to close
        self.put_messge_in_q(CloseMessage())

        # We cannot close the file at this moment because their might still be
        # messages in the queue to write

        self.closed = True

        LOGGER.debug("OfflineStreamer has been closed")

    def _after_run(self):
        # Close the messages files once we are sure we won't write in it
        # anymore
        self.file.close()

    def _loop(self):
        """
        A single loop of running
        """
        try:
            messages = self.getn(1)

            if messages and isinstance(messages[0], CloseMessage):
                return messages[0]

            if messages is not None:
                LOGGER.debug(
                    "Got %d messages, %d still in queue",
                    len(messages),
                    self.messages.qsize(),
                )

                for message in messages:
                    if isinstance(message, UploadFileMessage):
                        self._process_upload_message(message)
                    elif isinstance(message, Message):
                        self._process_ws_message(message)

        except Exception:
            LOGGER.debug("Unknown streaming error", exc_info=True)

    def _process_upload_message(self, message):
        # Create the file on disk
        tmpfile = tempfile.NamedTemporaryFile(dir=self.tmp_dir, delete=False)
        tmpfile.close()
        # Then move the original file to the newly create file
        shutil.move(message.file_path, tmpfile.name)
        message.file_path = basename(tmpfile.name)

        msg_json = message.repr_json()
        data = {"type": "file_upload", "payload": msg_json}
        self.file.write(compact_json(data) + "\n")
        self.file.flush()

    def _process_ws_message(self, message):
        msg_json = message.repr_json()

        data = {"type": "ws_msg", "payload": msg_json}
        self.file.write(compact_json(data) + "\n")
        self.file.flush()

    def wait_for_finish(self):
        """ Blocks the experiment from exiting until all data was sent to server OR 30 seconds passed."""

        msg = "Uploading stats to Comet before program termination (may take several seconds)"
        LOGGER.info(msg)

        # Wait maximum 2 minutes
        self._wait_for_empty(30)

        if not self.messages.empty():
            msg = "Still uploading stats to Comet before program termination (may take several seconds)"
            LOGGER.info(msg)
            self._wait_for_empty(30)

            if not self.messages.empty():
                self._wait_for_empty(60, verbose=True, sleep_time=5)

        if not self.messages.empty():
            remaining = self.messages.qsize()
            LOGGER.error(
                "Comet failed to send all the data back (%s messages)", remaining
            )

        # Also wait for the thread to finish to be sure that all messages are
        # written to the messages file
        self.join(None)

        if self.isAlive():
            LOGGER.debug(
                "OfflineStreamer didn't finished in time, messages files might be incomplete"
            )
            return False
        else:
            LOGGER.debug("OfflineStreamer finished in time")
            return True

    def _wait_for_empty(self, timeout, verbose=False, sleep_time=1):
        """ Wait up to TIMEOUT seconds for the messages queue to be empty
        """
        end_time = time.time() + timeout

        while not self.messages.empty() and time.time() < end_time:
            if verbose is True:
                LOGGER.info("%d messages remaining to upload", self.messages.qsize())
            time.sleep(sleep_time)


INFINITY = float("inf")


def fix_special_floats(value, _inf=INFINITY, _neginf=-INFINITY):
    """ Fix out of bounds floats (like infinity and -infinity) and Not A
    Number.
    Returns either a fixed value that could be JSON encoded or the original
    value.
    """

    try:
        # Check if the value is Nan, equivalent of math.isnan
        if isnan(value):
            return "NaN"

        elif value == _inf:
            return "Infinity"

        elif value == _neginf:
            return "-Infinity"

    except Exception:
        # Value cannot be compared
        return value

    return value


class Message(object):
    """
    A bean used to send messages to the server over websockets.
    """

    def __init__(self, context=None):
        self.context = context
        self.local_timestamp = local_timestamp()

        # The following attributes are optional
        self.metric = None
        self.param = None
        self.params = None
        self.graph = None
        self.code = None
        self.stdout = None
        self.stderr = None
        self.offset = None
        self.fileName = None
        self.env_details = None
        self.html = None
        self.htmlOverride = None
        self.installed_packages = None
        self.os_packages = None
        self.log_other = None
        self.gpu_static_info = None
        self.git_meta = None
        self.log_dependency = None
        self.log_system_info = None
        self.context = context

    def set_log_other(self, key, value):
        self.log_other = {"key": key, "val": value}

    def set_log_dependency(self, name, version):
        self.log_dependency = {"name": name, "version": version}

    def set_system_info(self, key, value):
        self.log_system_info = {"key": key, "value": value}

    def set_installed_packages(self, val):
        self.installed_packages = val

    def set_os_packages(self, val):
        self.os_packages = val

    def set_offset(self, val):
        self.offset = val

    def set_metric(self, name, value, step=None):
        safe_value = fix_special_floats(value)
        self.metric = {"metricName": name, "metricValue": safe_value, "step": step}

    def set_html(self, value):
        self.html = value

    def set_htmlOverride(self, value):
        self.htmlOverride = value

    def set_param(self, name, value, step=None):
        safe_value = fix_special_floats(value)
        self.param = {"paramName": name, "paramValue": safe_value, "step": step}

    def set_params(self, name, values, step=None):
        safe_values = list(map(fix_special_floats, values))
        self.params = {"paramName": name, "paramValue": safe_values, "step": step}

    def set_graph(self, graph):
        self.graph = graph

    def set_code(self, code):
        self.code = code

    def set_stdout(self, line):
        self.stdout = line
        self.stderr = False

    def set_stderr(self, line):
        self.stdout = line
        self.stderr = True

    def set_env_details(self, details):
        self.env_details = details

    def set_filename(self, fname):
        self.fileName = fname

    def set_gpu_static_info(self, info):
        self.gpu_static_info = info

    def set_git_metadata(self, metadata):
        self.git_meta = metadata

    def to_json(self):
        json_re = json.dumps(
            self.repr_json(), sort_keys=True, indent=4, cls=NestedEncoder
        )
        return json_re

    def repr_json(self):
        return self.__dict__

    def __repr__(self):
        filtered_dict = [(key, value) for key, value in self.__dict__.items() if value]
        string = ", ".join("%r=%r" % item for item in filtered_dict)
        return "Message(%s)" % string

    def __str__(self):
        return self.to_json()

    def __len__(self):
        return len(self.to_json())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class UploadFileMessage(object):
    def __init__(self, file_path, upload_type, additional_params, clean=True):
        self.local_timestamp = local_timestamp()

        self.file_path = file_path
        self.upload_type = upload_type
        self.additional_params = additional_params
        self.clean = clean
        self.offset = None

    def set_offset(self, offset):
        self.offset = offset

    def repr_json(self):
        return self.__dict__


def get_cmd_args_dict():
    if len(sys.argv) > 1:
        try:
            return parse_cmd_args(sys.argv[1:])

        except ValueError:
            LOGGER.debug("Failed to parse argv values. Falling back to naive parsing.")
            return parse_cmd_args_naive(sys.argv[1:])


def parse_cmd_args_naive(to_parse):
    vals = {}
    if len(to_parse) > 1:
        for i, arg in enumerate(to_parse):
            vals["run_arg_%s" % i] = str(arg)

    return vals


def parse_cmd_args(argv_vals):
    """
    Parses the value of argv[1:] to a dictionary of param,value. Expects params name to start with a - or --
    and value to follow. If no value follows that param is considered to be a boolean param set to true.(e.g --test)
    Args:
        argv_vals: The sys.argv[] list without the first index (script name). Basically sys.argv[1:]

    Returns: Dictionary of param_names, param_values

    """

    def guess_type(s):
        import ast

        try:
            value = ast.literal_eval(s)
            return value

        except (ValueError, SyntaxError):
            return str(s)

    results = {}

    current_key = None
    for word in argv_vals:
        word = word.strip()
        prefix = 0

        if word[0] == "-":
            prefix = 1
            if len(word) > 1 and word[1] == "-":
                prefix = 2

            if current_key is not None:
                # if we found a new key but haven't found a value to the previous
                # key it must have been a boolean argument.
                results[current_key] = True

            current_key = word[prefix:]

        else:
            word = word.strip()
            if current_key is None:
                # we failed to parse the string. We think this is a value but we don't know what's the key.
                # fallback to naive parsing.
                raise ValueError("Failed to parse argv arguments")

            else:
                word = guess_type(word)
                results[current_key] = word
                current_key = None

    if current_key is not None:
        # last key was a boolean
        results[current_key] = True

    return results


def save_matplotlib_figure(figure=None):
    """ Try saving either the current global pyplot figure or the given one
    and return None in case of error.
    """
    # Get the right figure to upload
    if figure is None:
        import matplotlib.pyplot

        # Get current global figure
        figure = matplotlib.pyplot.gcf()

    # Check if the figure is empty or not
    axes = figure.gca()
    if axes.has_data() is False:
        # TODO DISPLAY BETTER ERROR MSG
        msg = (
            "Refuse to upload empty figure, please call log_figure before calling show"
        )
        LOGGER.warning(msg)
        raise TypeError(msg)

    # Save the file to a tempfile but don't delete it, the file uploader
    # thread will take care of it
    tmpfile = tempfile.NamedTemporaryFile(suffix=".svg", delete=False)
    figure.savefig(tmpfile, format="svg")

    return tmpfile.name


def generate_guid():
    """ Generate a GUID
    """
    return uuid.uuid4().hex


GUID_REGEX = re.compile(r"^[0-9a-f]{32}$")


def is_valid_guid(guid):
    """ Validate a GUID; returns True or False
    """
    # The compiled regex is cached
    return isinstance(guid, str) and (
        (GUID_REGEX.match(guid) is not None)
        or (guid[:4] == "rest" and GUID_REGEX.match(guid[4:]) is not None)
    )


def get_api_key(api_key, config):
    if api_key is None:
        return config["comet.api_key"]
    else:
        return api_key


def get_ws_url(ws_server_from_backend, config):
    """ Allow users to override the WS url from the backend using the usual
    config mechanism
    """
    ws_server_from_config = config["comet.ws_url_override"]
    if ws_server_from_config is None:
        return ws_server_from_backend
    else:
        return ws_server_from_config


def get_previous_experiment(previous_experiment, config):
    if previous_experiment is None:
        return config["comet.experiment_key"]
    else:
        return previous_experiment


def get_rest_api_key(rest_api_key, config):
    if rest_api_key is None:
        return config["comet.rest_api_key"]

    else:
        return rest_api_key


def format_url(prefix, **query_arguments):
    if prefix is None:
        return None

    splitted = list(urlsplit(prefix))

    splitted[3] = urlencode(query_arguments)

    return urlunsplit(splitted)
