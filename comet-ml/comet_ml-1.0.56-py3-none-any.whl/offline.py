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
Author: Boris Feld

This module contains the code related to offline feature

"""
import json
import logging
import os
import os.path
import shutil
import tempfile
import traceback
import zipfile
from os.path import dirname, join
from zipfile import ZipFile

from jsonschema import ValidationError
from jsonschema.validators import validator_for

from ._logging import (
    OFFLINE_EXPERIMENT_ALREADY_UPLOADED,
    OFFLINE_EXPERIMENT_END,
    OFFLINE_EXPERIMENT_INVALID_UPLOAD_MSG,
    OFFLINE_EXPERIMENT_INVALID_WS_MSG,
    OFFLINE_EXPERIMENT_TEMPORARY_DIRECTORY,
    OFFLINE_SENDER_ENDS,
    OFFLINE_SENDER_STARTS,
)
from ._reporting import (
    EXPERIMENT_CREATED,
    OFFLINE_INVALID_UPLOAD_MSG,
    OFFLINE_INVALID_WS_MSG,
)
from .comet import OfflineStreamer, generate_guid, get_api_key
from .config import get_config
from .connection import (
    RestServerConnection,
    WebSocketConnection,
    format_messages_for_ws,
    get_backend_address,
)
from .exceptions import ExperimentAlreadyUploaded, InvalidOfflineDirectory
from .experiment import BaseExperiment
from .feature_toggles import FeatureToggles, get_feature_toggle_overrides
from .file_uploader import upload_file_thread
from .metrics import MetricsSampler
from .utils import local_timestamp

LOGGER = logging.getLogger(__name__)


class OfflineExperiment(BaseExperiment):
    def __init__(
        self,
        project_name=None,
        team_name=None,
        workspace=None,
        log_code=True,
        log_graph=True,
        auto_param_logging=True,
        auto_metric_logging=True,
        parse_args=True,
        auto_output_logging="default",
        log_env_details=True,
        log_git_metadata=True,
        log_git_patch=True,
        disabled=False,
        offline_directory=None,
        log_env_gpu=True,
        log_env_host=True,
        api_key=None,  # Optional, except for on-line operations
    ):
        """
        Creates a new experiment on the Comet.ml frontend.
        Args:
            project_name: Optional. Send your experiment to a specific project. Otherwise will be sent to `Uncategorized Experiments`.
                             If project name does not already exists Comet.ml will create a new project.
            team_name: Deprecated. Use workspace instead.
            workspace: Optional. Attach an experiment to a project that belongs to this workspace
            log_code: Default(True) - allows you to enable/disable code logging
            log_graph: Default(True) - allows you to enable/disable automatic computation graph logging.
            auto_param_logging: Default(True) - allows you to enable/disable hyper parameters logging
            auto_metric_logging: Default(True) - allows you to enable/disable metrics logging
            parse_args: Default(True) - allows you to enable/disable automatic parsing of CLI arguments
            auto_output_logging: Default("native") - allows you to select
                which output logging mode to use. The default is `"native"`
                which will log all output even when it originated from a C
                native library. You can also pass `"simple"` which will work
                only for output made by Python code. If you want to disable
                automatic output logging, you can pass `None`.
            log_env_details: Default(True) - log various environment
                informations in order to identify where the script is running
            log_env_gpu: Default(True) - allow you to enable/disable the
                automatic collection of gpu details and metrics (utilization, memory usage etc..).
                `log_env_details` must also be true.
            log_env_host: Default(True) - allow you to enable/disable the
                automatic collection of host information (ip, hostname, python version, user etc...).
                `log_env_details` must also be true.
            log_git_metadata: Default(True) - allow you to enable/disable the
                automatic collection of git details
            disabled: Default(False) - allows you to disable all network
                communication with the Comet.ml backend. It is useful when you
                just needs to works on your machine-learning scripts and need
                to relaunch them several times at a time.
            offline_directory: the directory used to save the offline archive
                for the experiment.
        """
        self.tmpdir = tempfile.mkdtemp()
        self.config = get_config()
        self.api_key = get_api_key(
            api_key, self.config
        )  # optional, except for on-line operations

        if offline_directory is None:
            offline_directory = self.config["comet.offline_directory"]

        if offline_directory is None:
            raise ValueError("OfflineExperiment needs an offline directory")

        self.offline_directory = offline_directory

        # Start and ends time
        self.start_time = None
        self.stop_time = None

        super(OfflineExperiment, self).__init__(
            project_name,
            team_name,
            workspace,
            log_code,
            log_graph,
            auto_param_logging,
            auto_metric_logging,
            parse_args,
            auto_output_logging,
            log_env_details,
            log_git_metadata,
            log_git_patch,
            disabled,
            log_env_gpu,
            log_env_host,
        )

        if not disabled:
            # Check that the offline directory is usable
            try:
                # Try to create the archive now
                zipfile = self._get_offline_archive(offline_directory, self.id)
                # Close the file handle, it will be reopened later
                zipfile.close()
            except (OSError, IOError) as exc:
                raise InvalidOfflineDirectory(self.offline_directory, str(exc))

        if disabled is not True:
            self._start()

            if self.alive is True:
                self._report(event_name=EXPERIMENT_CREATED)

    def display(self, *args, **kwargs):
        """ Do nothing
        """
        pass

    def _start(self):
        self.start_time = local_timestamp()
        super(OfflineExperiment, self)._start()

    def _write_experiment_meta_file(self):
        meta_file_path = join(self.tmpdir, "experiment.json")
        meta = {
            "auto_metric_logging": self.auto_metric_logging,
            "auto_output_logging": self.auto_output_logging,
            "auto_param_logging": self.auto_param_logging,
            "disabled": self.disabled,
            "feature_toggles_overrides": get_feature_toggle_overrides(),
            "log_code": self.log_code,
            "log_env_details": self.log_env_details,
            "log_git_metadata": self.log_git_metadata,
            "log_graph": self.log_graph,
            "parse_args": self.parse_args,
            "project_name": self.project_name,
            "start_time": self.start_time,
            "stop_time": self.stop_time,
            "tags": self.get_tags(),
            "workspace": self.workspace,
            "offline_id": self.id,
        }
        with open(meta_file_path, "w") as f:
            json.dump(meta, f)

    def _get_offline_archive(self, directory, name):
        # ZIP the saved informations
        mode = 0o700
        try:
            os.mkdir(self.offline_directory, mode)
        except os.error:
            pass

        file_path = self._offline_zip_path(directory, name)
        return ZipFile(file_path, "w")

    def _mark_as_ended(self):
        if not self.alive:
            LOGGER.debug("Skipping creating the offline archive as we are not alive")
            return

        LOGGER.info("Starting saving the offline archive")
        self.stop_time = local_timestamp()

        self._write_experiment_meta_file()

        try:
            zipfile = self._get_offline_archive(self.offline_directory, self.id)
        except (OSError, IOError) as exc:
            # Use a temporary directory if we came so far to not lose the informations
            old_dir = self.offline_directory
            self.offline_directory = tempfile.mkdtemp()
            zipfile = self._get_offline_archive(self.offline_directory, self.id)
            LOGGER.warning(
                OFFLINE_EXPERIMENT_TEMPORARY_DIRECTORY,
                old_dir,
                str(exc),
                self.offline_directory,
            )

        for file in os.listdir(self.tmpdir):
            zipfile.write(os.path.join(self.tmpdir, file), file)

        zipfile.close()

        # Clean the tmpdir to avoid filling up the disk
        try:
            shutil.rmtree(self.tmpdir)
        except OSError:
            # We made our best effort to clean ourselves
            msg = "Error cleaning offline experiment tmpdir %r"
            LOGGER.debug(msg, self.tmpdir, exc_info=True)

        # Display the full command to upload the offline experiment
        LOGGER.info(OFFLINE_EXPERIMENT_END, zipfile.filename)

    def _offline_zip_path(self, directory, name):
        return os.path.join(directory, "%s.zip" % name)

    def _setup_streamer(self):
        """
        Initialize the streamer and feature flags.
        """
        # Initiate the streamer
        self.streamer = OfflineStreamer(self.tmpdir, 0)

        # Start streamer thread.
        self.streamer.start()

        self.feature_toggles = FeatureToggles({}, self.config)

        # Mark the experiment as alive
        return True

    def _report(self, *args, **kwrags):
        # TODO WHAT TO DO WITH REPORTING?
        pass

    def _get_experiment_url(self):
        return "[OfflineExperiment will get URL after upload]"

    def _upload_file_like(
        self, file_data, upload_type, max_size, url_params, too_big_log_msg, copy_to_tmp
    ):
        if not copy_to_tmp:
            msg = (
                "Overriding copy_to_tmp to force writing in on disk for offline storage"
            )
            LOGGER.warning(msg)
            copy_to_tmp = True

        super(OfflineExperiment, self)._upload_file_like(
            file_data, upload_type, max_size, url_params, too_big_log_msg, copy_to_tmp
        )


def get_validator(filename, allow_additional_properties=True):
    with open(join(dirname(__file__), join("schemas", filename))) as schema_file:
        schema = json.load(schema_file)

    if not allow_additional_properties:
        schema["additionalProperties"] = False

    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    return validator_class(schema)


def get_experiment_file_validator(allow_additional_properties=True):
    return get_validator("offline-experiment.schema.json", allow_additional_properties)


def get_ws_msg_validator(allow_additional_properties=True):
    return get_validator("offline-ws-msg.schema.json", allow_additional_properties)


def get_upload_msg_validator(allow_additional_properties=True):
    return get_validator(
        "offline-file-upload-msg.schema.json", allow_additional_properties
    )


def unzip_offline_archive(offline_archive_path):
    temp_dir = tempfile.mkdtemp()

    zip_file = zipfile.ZipFile(offline_archive_path, mode="r")

    # Extract the archive
    zip_file.extractall(temp_dir)

    return temp_dir


class OfflineSender(object):
    def __init__(self, api_key, offline_dir, force_reupload=False):
        self.config = get_config()
        self.api_key = api_key
        self.offline_dir = offline_dir
        self.force_reupload = force_reupload
        self.counter = 0

        # Validators
        self.experiment_file_validator = get_experiment_file_validator()
        self.ws_msg_validator = get_ws_msg_validator()
        self.upload_msg_validator = get_upload_msg_validator()

        self.server_address = get_backend_address()

        self._read_experiment_file()

        self.connection = RestServerConnection(
            self.api_key, self.experiment_id, None, self.server_address
        )
        self.ws_connection = None
        self.focus_link = None
        self.upload_threads = []

    def send(self):
        self._handshake()

        self._status_report_start()

        LOGGER.info(OFFLINE_SENDER_STARTS)

        self._send_messages()

        self._status_report_end()

        self._send_start_ends_time()

    def _read_experiment_file(self):
        with open(join(self.offline_dir, "experiment.json")) as experiment_file:
            metadata = json.load(experiment_file)

        self.experiment_file_validator.validate(metadata)

        if self.force_reupload is True:
            self.experiment_id = generate_guid()
        else:
            self.experiment_id = metadata.get("offline_id")

            # Offline experiments created with old versions of the SDK will be
            # missing this field, so generate a new one if that's the case
            if not self.experiment_id:
                self.experiment_id = generate_guid()

        self.project_name = metadata["project_name"]
        self.start_time = metadata["start_time"]
        self.stop_time = metadata["stop_time"]
        self.tags = metadata["tags"]
        self.workspace = metadata["workspace"]

    def _handshake(self):
        run_id_results = self.connection.get_run_id(
            self.project_name, self.workspace, offline=True
        )

        (
            self.run_id,
            self.ws_url,
            self.project_id,
            self.is_github,
            self.focus_link,
            self.upload_limit,
            feature_toggles,
            initial_offset,
            upload_web_asset_url_prefix,
            upload_web_image_url_prefix,
            upload_api_asset_url_prefix,
            upload_api_image_url_prefix,
        ) = run_id_results

        # Send tags if present
        if self.tags:
            self.connection.add_tags(self.tags)

        self.ws_connection = WebSocketConnection(self.ws_url, self.connection)
        self.ws_connection.start()
        self.ws_connection.wait_for_connection()

    def _send_messages(self):
        i = 0

        # Samples down the metrics
        sampling_size = self.config["comet.offline_sampling_size"]

        LOGGER.debug("Sampling metrics to %d values per metric name", sampling_size)

        sampler = MetricsSampler(sampling_size)

        with open(join(self.offline_dir, "messages.json")) as messages_files:
            for i, line in enumerate(messages_files):
                try:
                    message = json.loads(line)

                    LOGGER.debug("Message %r", message)

                    message_type = message["type"]

                    if message_type == "ws_msg":
                        message_payload = message["payload"]
                        message_metric = message_payload["metric"]

                        if message_metric:
                            sampler.sample_metric(message_payload)
                        else:
                            self._process_ws_msg(message_payload)
                    elif message_type == "file_upload":
                        self._process_upload_message(message)
                except Exception:
                    LOGGER.warning("Error processing line %d", i + 1, exc_info=True)

        # Then send the sampled metrics
        samples = sampler.get_samples()
        for metric in samples:
            try:
                self._process_ws_msg(metric)
            except Exception:
                LOGGER.warning("Error processing metric", exc_info=True)

        LOGGER.debug("Done sending %d messages", i)

    def _process_ws_msg(self, message):
        try:
            self.ws_msg_validator.validate(message)
        except ValidationError:
            tb = traceback.format_exc()
            LOGGER.warning(OFFLINE_EXPERIMENT_INVALID_WS_MSG, exc_info=True)
            self.connection.report(event_name=OFFLINE_INVALID_WS_MSG, err_msg=tb)

        # Inject api key and run_id
        message["apiKey"] = self.api_key
        message["runId"] = self.run_id
        message["projectId"] = self.project_id
        message["experimentKey"] = self.experiment_id

        to_send = format_messages_for_ws([message])

        self.ws_connection.send(to_send)

    def _process_upload_message(self, message):
        message = message["payload"]

        try:
            self.upload_msg_validator.validate(message)
        except ValidationError:
            tb = traceback.format_exc()
            LOGGER.warning(OFFLINE_EXPERIMENT_INVALID_UPLOAD_MSG, exc_info=True)
            self.connection.report(event_name=OFFLINE_INVALID_UPLOAD_MSG, err_msg=tb)

        # Compute the url from the upload type
        url = self.connection.get_upload_url(message["upload_type"])

        additional_params = message["additional_params"] or {}
        additional_params["runId"] = self.run_id

        upload_thread = upload_file_thread(
            project_id=self.project_id,
            experiment_id=self.experiment_id,
            file_path=join(self.offline_dir, message["file_path"]),
            upload_endpoint=url,
            api_key=self.api_key,
            additional_params=additional_params,
            clean=True,
        )
        self.upload_threads.append(upload_thread)
        LOGGER.debug("Processing uploading message done")
        LOGGER.debug("Upload threads %s", self.upload_threads)

    def _status_report_start(self):
        self.connection.update_experiment_status(
            self.run_id, self.project_id, True, offline=True
        )

    def _status_report_end(self):
        self.connection.update_experiment_status(
            self.run_id, self.project_id, False, offline=True
        )

    def _send_start_ends_time(self):
        self.connection.offline_experiment_start_end_time(
            self.run_id, self.start_time, self.stop_time
        )

    def _get_experiment_url(self):
        if self.focus_link:
            return self.focus_link + self.experiment_id

        return ""

    def close(self):
        if self.ws_connection is not None:
            self.ws_connection.close()
            self.ws_connection.wait_for_finish()

        for thread in self.upload_threads:
            thread.join()
        LOGGER.debug("Upload threads %r", self.upload_threads)

        LOGGER.info(OFFLINE_SENDER_ENDS, self._get_experiment_url())


def upload_single_offline_experiment(offline_archive_path, api_key, force_reupload):
    unzipped_directory = unzip_offline_archive(offline_archive_path)
    sender = OfflineSender(api_key, unzipped_directory, force_reupload=force_reupload)
    try:
        sender.send()
        sender.close()
        return True
    except ExperimentAlreadyUploaded:
        LOGGER.error(OFFLINE_EXPERIMENT_ALREADY_UPLOADED, offline_archive_path)
        return False
    finally:
        try:
            shutil.rmtree(unzipped_directory)
        except OSError:
            # We made our best effort to clean after ourselves
            msg = "Failed to clean the Offline sender tmpdir %r"
            LOGGER.debug(msg, unzipped_directory, exc_info=True)


def main_upload(archives, force_reupload):
    upload_count = 0
    fail_count = 0

    # Common code
    config = get_config()
    api_key = get_api_key(None, config)

    for filename in archives:
        LOGGER.info("Attempting to upload '%s'...", filename)
        try:
            success = upload_single_offline_experiment(
                filename, api_key, force_reupload
            )

            if success:
                upload_count += 1
            else:
                fail_count += 1

        except KeyboardInterrupt:
            break
        except Exception:
            LOGGER.error(
                "    Upload failed", exc_info=True, extra={"show_traceback": True}
            )
            fail_count += 1
        else:
            LOGGER.info("    done!")
    LOGGER.info("Number of uploaded experiments: %s", upload_count)
    if fail_count > 0:
        LOGGER.info("Number of failed experiment uploads: %s", fail_count)
