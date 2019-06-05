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

from __future__ import print_function

import json
import logging
import ssl
import sys
import threading
import time

import comet_ml
import requests
import six
import websocket
from comet_ml import config
from comet_ml._logging import WS_ON_CLOSE_MSG, WS_ON_OPEN_MSG, WS_SSL_ERROR_MSG
from comet_ml._reporting import WS_ON_CLOSE, WS_ON_ERROR, WS_ON_OPEN
from comet_ml.config import DEFAULT_UPLOAD_SIZE_LIMIT, get_config
from comet_ml.exceptions import (
    ExperimentAlreadyUploaded,
    InvalidAPIKey,
    InvalidWorkspace,
    ProjectNameEmpty,
)
from comet_ml.json_encoder import NestedEncoder
from comet_ml.utils import local_timestamp
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if six.PY2:
    from urlparse import urlparse
    from urllib import getproxies
else:
    from urllib.parse import urlparse
    from urllib.request import getproxies


TIMEOUT = 10

OPTIMIZER_SESSION = None
INITIAL_BEAT_DURATION = 10000  # 10 second

LOGGER = logging.getLogger(__name__)


def _comet_version():
    try:
        version_num = comet_ml.__version__
    except NameError:
        version_num = None

    return version_num


def get_retry_strategy():

    # The total backoff sleeping time is computed like that:
    # backoff = 2
    # total = 3
    # s = lambda b, i: b * (2 ** (i - 1))
    # sleep = sum(s(backoff, i) for i in range(1, total + 1))

    return Retry(
        total=3,
        backoff_factor=2,
        method_whitelist=False,
        status_forcelist=[500, 502, 503, 504],
    )  # Will wait up to 24s


def get_backend_address():
    config = get_config()
    return config["comet.url_override"]


def get_optimizer_address(config):
    return config["comet.optimization_override"]


def get_backend_session(backend_address=None, retry_strategy=None):
    session = requests.Session()

    # Setup retry strategy if asked
    if retry_strategy is not None and backend_address is not None:
        session.mount(backend_address, HTTPAdapter(max_retries=retry_strategy))

    # Setup HTTP allow header if configured
    config = get_config()
    allow_header_name = config["comet.allow_header.name"]
    allow_header_value = config["comet.allow_header.value"]

    if allow_header_name and allow_header_value:
        session.headers[allow_header_name] = allow_header_value

    return session


def get_optimizer_session():
    global OPTIMIZER_SESSION
    if OPTIMIZER_SESSION is None:
        OPTIMIZER_SESSION = requests.Session()

    return requests.Session()


def json_post(url, session, headers, body, timeout):
    response = session.post(
        url=url, data=json.dumps(body), headers=headers, timeout=timeout
    )

    response.raise_for_status()
    return response


def format_messages_for_ws(messages):
    """ Encode a list of messages into JSON
    """
    messages_arr = []
    for message in messages:
        payload = {}
        # make sure connection is actually alive
        if message["stdout"] is not None:
            payload["stdout"] = message
        else:
            payload["log_data"] = message

        messages_arr.append(payload)

    data = json.dumps(messages_arr, cls=NestedEncoder, allow_nan=False)
    LOGGER.debug("ENCODED DATA %r", data)
    return data


class RestServerConnection(object):
    """
    A static class that handles the connection with the server.
    """

    def __init__(self, api_key, experiment_id, optimization_id, server_address):
        self.api_key = api_key
        self.experiment_id = experiment_id
        self.optimization_id = optimization_id

        # Set once get_run_id is called
        self.run_id = None
        self.project_id = None

        self.server_address = server_address

        self.session = get_backend_session()
        self.retry_session = get_backend_session(
            self.server_address, retry_strategy=get_retry_strategy()
        )

        self.upload_type_url_map = {
            "asset": asset_upload_url(),
            "visualization": visualization_upload_url(),
            "git-patch": get_git_patch_upload_endpoint(),
        }

    def close(self):
        self.session.close()
        self.retry_session.close()

    def heartbeat(self):
        """ Inform the backend that we are still alive
        """
        LOGGER.debug("Doing an heartbeat")
        return self.update_experiment_status(self.run_id, self.project_id, True)

    def update_experiment_status(self, run_id, project_id, is_alive, offline=False):
        endpoint_url = self.server_address + "status-report/update"
        headers = {"Content-Type": "application/json;charset=utf-8"}

        payload = {
            "apiKey": self.api_key,
            "runId": run_id,
            "experimentKey": self.experiment_id,
            "projectId": project_id,
            "optimizationId": self.optimization_id,
            "is_alive": is_alive,
            "local_timestamp": local_timestamp(),
            "offline": offline,
        }

        LOGGER.debug("Experiment status update with payload: %s", payload)

        r = self.session.post(
            url=endpoint_url, data=json.dumps(payload), headers=headers, timeout=TIMEOUT
        )

        if r.status_code != 200:
            raise ValueError(r.content)

        data = r.json()
        LOGGER.debug("Update experiment status response payload: %r", data)
        beat_duration = data.get("is_alive_beat_duration_millis")

        if beat_duration is None:
            raise ValueError("Missing heart-beat duration")

        gpu_monitor_duration = data.get("gpu_monitor_interval_millis")

        if gpu_monitor_duration is None:
            raise ValueError("Missing gpu-monitor duration")

        pending_rpcs = data.get("pending_rpcs", False)

        return beat_duration, gpu_monitor_duration, pending_rpcs

    def get_run_id(self, project_name, workspace, offline=False):
        """
        Gets a new run id from the server.
        :param api_key: user's API key
        :return: run_id - String
        """
        endpoint_url = get_run_id_url(self.server_address)
        headers = {"Content-Type": "application/json;charset=utf-8"}

        # We used to pass the team name as second parameter then we migrated
        # to workspaces. We keep using the same payload field as compatibility
        # is ensured by the backend and old SDK version will still uses it
        # anyway
        payload = {
            "apiKey": self.api_key,
            "local_timestamp": local_timestamp(),
            "experimentKey": self.experiment_id,
            "offline": offline,
            "optimizationId": self.optimization_id,
            "projectName": project_name,
            "teamName": workspace,
            "libVersion": _comet_version(),
        }

        LOGGER.debug("Get run id URL: %s", endpoint_url)
        r = self.retry_session.post(
            url=endpoint_url, data=json.dumps(payload), headers=headers, timeout=TIMEOUT
        )

        if r.status_code != 200:
            if r.status_code == 400:
                # Check if the api key was invalid
                data = r.json()  # Raise a ValueError if failing
                code = data.get("sdk_error_code")
                if code == 90212:
                    raise InvalidAPIKey(self.api_key)

                elif code == 90219:
                    raise InvalidWorkspace(workspace)

                elif code == 98219:
                    raise ProjectNameEmpty()

                elif code == 90999:
                    raise ExperimentAlreadyUploaded(self.experiment_id)

            raise ValueError(r.content)

        res_body = json.loads(r.content.decode("utf-8"))

        LOGGER.debug("New run response body: %s", res_body)

        return self._parse_run_id_res_body(res_body)

    def get_old_run_id(self, previous_experiment):
        """
        Gets a run id from an existing experiment.
        :param api_key: user's API key
        :return: run_id - String
        """
        endpoint_url = self.server_address + "logger/get/run"
        headers = {"Content-Type": "application/json;charset=utf-8"}

        payload = {
            "apiKey": self.api_key,
            "local_timestamp": local_timestamp(),
            "previousExperiment": previous_experiment,
            "libVersion": _comet_version(),
        }
        LOGGER.debug("Get old run id URL: %s", endpoint_url)
        r = self.retry_session.post(
            url=endpoint_url, data=json.dumps(payload), headers=headers, timeout=TIMEOUT
        )

        if r.status_code != 200:
            if r.status_code == 400:
                # Check if the api key was invalid
                data = r.json()  # Raise a ValueError if failing
                if data.get("sdk_error_code") == 90212:
                    raise InvalidAPIKey(self.api_key)

            raise ValueError(r.content)

        res_body = json.loads(r.content.decode("utf-8"))

        LOGGER.debug("Old run response body: %s", res_body)

        return self._parse_run_id_res_body(res_body)

    def copy_run(self, previous_experiment, copy_step):
        """
        Gets a run id from an existing experiment.
        :param api_key: user's API key
        :return: run_id - String
        """
        endpoint_url = copy_experiment_url(self.server_address)
        headers = {"Content-Type": "application/json;charset=utf-8"}

        payload = {
            "apiKey": self.api_key,
            "copiedExperimentKey": previous_experiment,
            "newExperimentKey": self.experiment_id,
            "stepToCopyTo": copy_step,
            "localTimestamp": local_timestamp(),
            "libVersion": _comet_version(),
        }
        LOGGER.debug("Copy run URL: %s", endpoint_url)
        r = self.retry_session.post(
            url=endpoint_url, data=json.dumps(payload), headers=headers, timeout=TIMEOUT
        )

        if r.status_code != 200:
            if r.status_code == 400:
                # Check if the api key was invalid
                data = r.json()  # Raise a ValueError if failing
                if data.get("sdk_error_code") == 90212:
                    raise InvalidAPIKey(self.api_key)

            raise ValueError(r.content)

        res_body = json.loads(r.content.decode("utf-8"))

        LOGGER.debug("Copy run response body: %s", res_body)

        return self._parse_run_id_res_body(res_body)

    def _parse_run_id_res_body(self, res_body):
        run_id_server = res_body["runId"]
        ws_server = res_body["ws_url"]

        project_id = res_body.get("project_id", None)

        is_github = bool(res_body.get("githubEnabled", False))

        focus_link = res_body.get("focusUrl", None)

        upload_limit = res_body.get("upload_file_size_limit_in_mb", None)

        last_offset = res_body.get("lastOffset", 0)

        if not (isinstance(upload_limit, int) and upload_limit > 0):
            upload_limit = DEFAULT_UPLOAD_SIZE_LIMIT
        else:
            # The limit is given in Mb, convert it back in bytes
            upload_limit = upload_limit * 1024 * 1024

        res_msg = res_body.get("msg")
        if res_msg:
            LOGGER.info(res_msg)

        # Parse feature toggles
        feature_toggles = {}
        LOGGER.debug("Raw feature toggles %r", res_body.get("featureToggles", []))
        for toggle in res_body.get("featureToggles", []):
            try:
                feature_toggles[toggle["name"]] = bool(toggle["enabled"])
            except (KeyError, TypeError):
                LOGGER.debug("Invalid feature toggle: %s", toggle, exc_info=True)
        LOGGER.debug("Parsed feature toggles %r", feature_toggles)

        # Parse URL prefixes
        web_asset_url = res_body.get("cometWebAssetUrl", None)
        web_image_url = res_body.get("cometWebImageUrl", None)
        api_asset_url = res_body.get("cometRestApiAssetUrl", None)
        api_image_url = res_body.get("cometRestApiImageUrl", None)

        # Save run_id and project_id around
        self.run_id = run_id_server
        self.project_id = project_id

        return (
            run_id_server,
            ws_server,
            project_id,
            is_github,
            focus_link,
            upload_limit,
            feature_toggles,
            last_offset,
            web_asset_url,
            web_image_url,
            api_asset_url,
            api_image_url,
        )

    def report(self, event_name=None, err_msg=None):
        try:
            if event_name is not None:
                endpoint_url = notify_url(self.server_address)
                headers = {"Content-Type": "application/json;charset=utf-8"}
                # Automatically add the sdk_ prefix to the event name
                real_event_name = "sdk_{}".format(event_name)

                payload = {
                    "event_name": real_event_name,
                    "api_key": self.api_key,
                    "run_id": self.run_id,
                    "experiment_key": self.experiment_id,
                    "project_id": self.project_id,
                    "err_msg": err_msg,
                    "timestamp": local_timestamp(),
                }

                LOGGER.debug("Report notify URL: %s", endpoint_url)

                json_post(endpoint_url, self.session, headers, payload, TIMEOUT / 2)

        except Exception:
            LOGGER.debug("Error reporting", exc_info=True)
            pass

    def offline_experiment_start_end_time(self, run_id, start_time, stop_time):
        endpoint_url = offline_experiment_times_url(self.server_address)
        headers = {"Content-Type": "application/json;charset=utf-8"}

        payload = {
            "apiKey": self.api_key,
            "runId": run_id,
            "experimentKey": self.experiment_id,
            "startTimestamp": start_time,
            "endTimestamp": stop_time,
        }

        LOGGER.debug(
            "Offline experiment start time and end time update with payload: %s",
            payload,
        )

        r = self.session.post(
            url=endpoint_url, data=json.dumps(payload), headers=headers, timeout=TIMEOUT
        )

        if r.status_code != 200:
            raise ValueError(r.content)

        return None

    def add_tags(self, added_tags):
        endpoint_url = add_tags_url(self.server_address)
        headers = {"Content-Type": "application/json;charset=utf-8"}

        payload = {
            "apiKey": self.api_key,
            "experimentKey": self.experiment_id,
            "addedTags": added_tags,
        }

        LOGGER.debug("Add tags with payload: %s", payload)

        r = self.session.post(
            url=endpoint_url, data=json.dumps(payload), headers=headers, timeout=TIMEOUT
        )

        if r.status_code != 200:
            raise ValueError(r.content)

        return None

    def get_upload_url(self, upload_type):
        return self.server_address + self.upload_type_url_map[upload_type]

    def get_pending_rpcs(self):
        endpoint_url = pending_rpcs_url(self.server_address)
        headers = {"Content-Type": "application/json;charset=utf-8"}

        payload = {"apiKey": self.api_key, "experimentKey": self.experiment_id}

        LOGGER.debug("Get pending RPCS with payload: %s", payload)

        r = self.session.get(
            url=endpoint_url, params=payload, headers=headers, timeout=TIMEOUT
        )

        if r.status_code != 200:
            raise ValueError(r.content)

        res_body = json.loads(r.content.decode("utf-8"))

        return res_body

    def register_rpc(self, function_definition):
        endpoint_url = register_rpc_url(self.server_address)
        headers = {"Content-Type": "application/json;charset=utf-8"}

        payload = {"apiKey": self.api_key, "experimentKey": self.experiment_id}
        # We might replace this payload.update by defining the exact
        # parameters once the payload body has been stabilized
        payload.update(function_definition)

        LOGGER.debug("Register RPC with payload: %s", payload)

        r = json_post(endpoint_url, self.session, headers, payload, TIMEOUT)

        if r.status_code != 200:
            raise ValueError(r.content)

        return None

    def send_rpc_result(self, callId, result, start_time, end_time):
        endpoint_url = rpc_result_url(self.server_address)
        headers = {"Content-Type": "application/json;charset=utf-8"}

        error = result.get("error", "")
        error_stacktrace = result.get("traceback", "")
        result = result.get("result", "")

        payload = {
            "apiKey": self.api_key,
            "experimentKey": self.experiment_id,
            "callId": callId,
            "result": result,
            "errorMessage": error,
            "errorStackTrace": error_stacktrace,
            "startTimeMs": start_time,
            "endTimeMs": end_time,
        }

        LOGGER.debug("Sending RPC result with payload: %s", payload)

        r = json_post(endpoint_url, self.session, headers, payload, TIMEOUT)

        if r.status_code != 200:
            raise ValueError(r.content)

        return None

    def send_new_symlink(self, project_name):
        endpoint_url = new_symlink_url(self.server_address)

        payload = {
            "apiKey": self.api_key,
            "experimentKey": self.experiment_id,
            "projectName": project_name,
        }

        headers = {"Content-Type": "application/json;charset=utf-8"}

        LOGGER.debug("new symlink: %s", payload)

        r = self.session.get(
            url=endpoint_url, params=payload, headers=headers, timeout=TIMEOUT
        )

        if r.status_code != 200:
            raise ValueError(r.content)


class Reporting(object):
    @staticmethod
    def report(
        event_name=None,
        api_key=None,
        run_id=None,
        experiment_key=None,
        project_id=None,
        err_msg=None,
        is_alive=None,
    ):

        try:
            if event_name is not None:
                server_address = get_backend_address()
                endpoint_url = notify_url(server_address)
                headers = {"Content-Type": "application/json;charset=utf-8"}
                # Automatically add the sdk_ prefix to the event name
                real_event_name = "sdk_{}".format(event_name)

                payload = {
                    "event_name": real_event_name,
                    "api_key": api_key,
                    "run_id": run_id,
                    "experiment_key": experiment_key,
                    "project_id": project_id,
                    "err_msg": err_msg,
                    "timestamp": local_timestamp(),
                }

                json_post(
                    endpoint_url, get_backend_session(), headers, payload, TIMEOUT / 2
                )

        except Exception:
            LOGGER.debug("Failing to report %s", event_name, exc_info=True)


class WebSocketConnection(threading.Thread):
    """
    Handles the ongoing connection to the server via Web Sockets.
    """

    def __init__(self, ws_server_address, connection):
        threading.Thread.__init__(self)
        self.priority = 0.2
        self.daemon = True
        self.name = "WebSocketConnection(%s)" % (ws_server_address)
        self.closed = False

        if config.DEBUG:
            websocket.enableTrace(True)

        self.address = ws_server_address

        self.config = get_config()

        self.allow_header_name = self.config["comet.allow_header.name"]
        self.allow_header_value = self.config["comet.allow_header.value"]

        LOGGER.debug("Creating a new WSConnection with url: %s", ws_server_address)

        self.ws = self.connect_ws(self.address)

        self.connection = connection

        self.last_error = None

    def is_connected(self):
        return getattr(self.ws.sock, "connected", False)

    def connect_ws(self, ws_server_address):
        header = []

        if self.allow_header_name and self.allow_header_value:
            header.append("%s: %s" % (self.allow_header_name, self.allow_header_value))

        ws = websocket.WebSocketApp(
            ws_server_address,
            header=header,
            on_message=lambda *args, **kwargs: self.on_message(*args, **kwargs),
            on_error=lambda *args, **kwargs: self.on_error(*args, **kwargs),
            on_close=lambda *args, **kwargs: self.on_close(*args, **kwargs),
        )
        ws.on_open = lambda *args, **kwargs: self.on_open(*args, **kwargs)
        return ws

    def run(self):
        while self.closed is False:
            try:
                self._loop()
            except Exception:
                LOGGER.debug("Run forever error", exc_info=True)
                # Avoid hammering the backend
                time.sleep(0.5)
        LOGGER.debug("WebSocketConnection has ended")

    def _loop(self):
        # Pass the default ping_timeout to avoid issues with websocket-client
        # >= 0.50.0
        http_proxy_host, http_proxy_port, http_proxy_auth, proxy_type = get_http_proxy()
        self.ws.run_forever(
            ping_timeout=10,
            http_proxy_host=http_proxy_host,
            http_proxy_port=http_proxy_port,
            http_proxy_auth=http_proxy_auth,
            proxy_type=proxy_type,
        )
        LOGGER.debug("Run forever has ended")

    def send(self, data, retry=5):
        """ Encode the messages into JSON and send them on the websocket
        connection
        """
        for i in range(retry):
            success = self._send(data)
            if success:
                return
            else:
                LOGGER.debug("Retry WS sending!")

        LOGGER.debug("Message %r failed to be sent", data)

    def close(self):
        LOGGER.debug("Closing %r", self)
        self.closed = True
        self.ws.close()

    def wait_for_finish(self, timeout=5):
        self.join(timeout)
        if self.isAlive():
            msg = "Websocket connection didn't closed properly after %d seconds"
            LOGGER.debug(msg, timeout)
        else:
            LOGGER.debug("Websocket connection correctly closed")

    def _send(self, data):
        if self.ws.sock:
            self.ws.send(data)
            LOGGER.debug("Sending data done, %r", data)
            return True

        else:
            LOGGER.debug("WS not ready for connection")
            self.wait_for_connection()
            return False

    def wait_for_connection(self, num_of_tries=20):
        """
        waits for the server connection
        Args:
            num_of_tries: number of times to try connecting before giving up

        Returns: True if succeeded to connect.

        """
        if not self.is_connected():
            counter = 0

            while not self.is_connected() and counter < num_of_tries:
                time.sleep(0.5)
                counter += 1

            if not self.is_connected():
                self.close()

                if self.last_error is not None:
                    # Process potential sources of errors
                    if isinstance(self.last_error[1], ssl.SSLError):
                        LOGGER.error(
                            WS_SSL_ERROR_MSG,
                            exc_info=self.last_error,
                            extra={"show_traceback": True},
                        )

                raise ValueError("Could not connect to server after multiple tries.")

        return True

    def on_open(self, ws):
        LOGGER.debug(WS_ON_OPEN_MSG)

        self.connection.report(event_name=WS_ON_OPEN, err_msg=WS_ON_OPEN_MSG)

    def on_message(self, ws, message):
        if message != "got msg":
            LOGGER.debug("WS msg: %s", message)

    def on_error(self, ws, error):
        error_type_str = type(error).__name__
        ignores = [
            "WebSocketBadStatusException",
            "error",
            "WebSocketConnectionClosedException",
            "ConnectionRefusedError",
            "BrokenPipeError",
        ]

        self.connection.report(event_name=WS_ON_ERROR, err_msg=repr(error))

        # Ignore some errors for auto-reconnecting
        if error_type_str in ignores:
            LOGGER.debug("Ignore WS error: %r", error, exc_info=True)
            return

        LOGGER.debug("WS on error: %r", error, exc_info=True)

        # Save error
        self.last_error = sys.exc_info()

    def on_close(self, *args, **kwargs):
        LOGGER.debug(WS_ON_CLOSE_MSG)
        self.connection.report(event_name=WS_ON_CLOSE, err_msg=WS_ON_CLOSE_MSG)


def notify_url(server_address):
    return server_address + "notify/event"


def visualization_upload_url():
    """ Return the URL to upload visualizations
    """
    return "visualizations/upload"


def asset_upload_url():
    return "asset/upload"


def get_git_patch_upload_endpoint():
    return "git-patch/upload"


def log_url(server_address):
    return server_address + "log/add"


def offline_experiment_times_url(server_address):
    return server_address + "status-report/offline-metadata"


def pending_rpcs_url(server_address):
    return server_address + "rpc/get-pending-rpcs"


def add_tags_url(server_address):
    return server_address + "tags/add-tags-to-experiment"


def register_rpc_url(server_address):
    return server_address + "rpc/register-rpc"


def rpc_result_url(server_address):
    return server_address + "rpc/save-rpc-result"


def new_symlink_url(server_address):
    return server_address + "symlink/new"


def get_run_id_url(server_address):
    return server_address + "logger/add/run"


def copy_experiment_url(server_address):
    return server_address + "logger/copy-steps-from-experiment"


def get_http_proxy():
    http_proxy_host = None
    http_proxy_port = None
    http_proxy_auth = None
    proxy_type = None
    proxies = getproxies()
    http_proxy = proxies.get("https")
    if http_proxy is not None:
        http_proxy_obj = urlparse(http_proxy)
        proxy_type = http_proxy_obj.scheme
        if http_proxy_obj.port is not None:
            http_proxy_port = str(http_proxy_obj.port)
        http_proxy_host = http_proxy_obj.hostname
        if http_proxy_obj.username or http_proxy_obj.password:
            http_proxy_auth = (http_proxy_obj.username, http_proxy_obj.password)
        LOGGER.debug("Using HTTPS_PROXY: %s:%s" % (http_proxy_host, http_proxy_port))
        if http_proxy_host is None:
            raise ValueError("Invalid https proxy format `%s`" % http_proxy)
    return http_proxy_host, http_proxy_port, http_proxy_auth, proxy_type


class OptimizerConnection(object):
    def __init__(self, headers, optimization_address):
        self.session = get_optimizer_session()
        self.headers = headers
        self.optimization_address = optimization_address

    def authenticate(self, api_key, optimization_id):
        data = {
            "optimizationId": optimization_id,
            "apiKey": api_key,
            "libVersion": _comet_version(),
        }

        response = self.session.post(
            self.optimization_address + "authenticate", json=data, headers=self.headers
        )
        response.raise_for_status()
        return response

    def create(self, pcs_content):
        files = {"file": pcs_content}
        response = self.session.post(
            self.optimization_address + "create", files=files, headers=self.headers
        )
        response.raise_for_status()
        return response

    def get_suggestion(self):
        response = self.session.get(
            self.optimization_address + "suggestion/", headers=self.headers
        )
        response.raise_for_status()
        return response

    def report_score(self, run_id, score):
        response = self.session.post(
            self.optimization_address + "value/%s" % run_id,
            json={"value": score},
            headers=self.headers,
        )
        response.raise_for_status()
        return response
