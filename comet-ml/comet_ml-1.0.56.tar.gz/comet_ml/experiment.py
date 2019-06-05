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

This module contains comet base Experiment code

"""
from __future__ import print_function

import atexit
import inspect
import io
import logging
import numbers
import os
import os.path
import shutil
import sys
import tempfile
import traceback
import types
from collections import defaultdict
from contextlib import contextmanager

import six
from six.moves._thread import get_ident

from ._logging import (
    ADD_TAGS_ERROR,
    ALREADY_IMPORTED_MODULES,
    EXPERIMENT_INVALID_STEP,
    EXPERIMENT_OPTIMIZER_API_KEY_MISMTACH_WARNING,
    GO_TO_DOCS_MSG,
    LOG_ASSET_FOLDER_ERROR,
    LOG_DATASET_ERROR,
    LOG_FIGURE_TOO_BIG,
    LOG_IMAGE_TOO_BIG,
    METRIC_ARRAY_WARNING,
    UPLOAD_ASSET_TOO_BIG,
    UPLOAD_FILE_OS_ERROR,
)
from ._reporting import EXPERIMENT_CREATION_FAILED, GIT_PATCH_GENERATION_FAILED
from .comet import (
    Message,
    UploadFileMessage,
    format_url,
    generate_guid,
    get_cmd_args_dict,
    save_matplotlib_figure,
)
from .config import (
    DEFAULT_ASSET_UPLOAD_SIZE_LIMIT,
    DEFAULT_UPLOAD_SIZE_LIMIT,
    get_config,
    get_global_experiment,
    get_global_optimizer,
    set_global_experiment,
)
from .console import get_std_logger
from .env_logging import get_env_details
from .exceptions import (
    CometException,
    FileIsTooBig,
    InterruptedExperiment,
    LambdaUnsupported,
    RPCFunctionAlreadyRegistered,
)
from .file_uploader import compress_git_patch
from .git_logging import find_git_patch, get_git_metadata
from .gpu_logging import (
    DEFAULT_GPU_MONITOR_INTERVAL,
    GPULoggingThread,
    convert_gpu_details_to_metrics,
    get_gpu_static_info,
    get_initial_gpu_metric,
    is_gpu_details_available,
)
from .rpc import call_remote_function
from .utils import (
    check_max_file_size,
    data_to_fp,
    image_data_to_file_like_object,
    is_list_like,
    is_valid_file_path,
    local_timestamp,
    read_unix_packages,
    write_file_like_to_tmp_file,
)

LOGGER = logging.getLogger(__name__)


class BaseExperiment(object):
    """
    Experiment is a unit of measurable research that defines a single run with some data/parameters/code/results.

    Creating an Experiment object in your code will report a new experiment to your Comet.ml project. Your Experiment
    will automatically track and collect many things and will also allow you to manually report anything.

    You can create multiple objects in one script (such as when looping over multiple hyper parameters).

    """

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
        log_env_gpu=True,
        log_env_host=True,
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
            log_git_patch: Default(True) - allow you to enable/disable the
                automatic collection of git patch
            disabled: Default(False) - allows you to disable all network
                communication with the Comet.ml backend. It is useful when you
                just needs to works on your machine-learning scripts and need
                to relaunch them several times at a time.
        """
        self.config = get_config()
        self._summary = {
            "data": {"url": None},
            "uploads": {"assets": 0, "figures": 0, "images": 0},
            "other": {},
            "metric": {},
        }

        self.project_name = (
            project_name if project_name else self.config["comet.project_name"]
        )

        if team_name is not None:
            LOGGER.warning(
                "The team_name argument is deprecated and will be removed after 2018/10/1. Please use the workspace "
                "argument instead. See additional information here: https://www.comet.ml/docs/workspaces/"
            )

        self.workspace = workspace if workspace is not None else team_name

        self.params = {}
        self.metrics = {}
        self.others = {}
        self.tags = set()

        self.log_code = log_code
        self.log_graph = log_graph
        self.auto_param_logging = auto_param_logging
        self.auto_metric_logging = auto_metric_logging
        self.parse_args = parse_args
        ## Default is "native" for regular environments, None for Jupyter:
        if auto_output_logging == "default":
            if self._in_jupyter_environment():
                self.auto_output_logging = None
            elif self._in_ipython_environment():
                self.auto_output_logging = None
            else:
                self.auto_output_logging = "native"
        else:
            self.auto_output_logging = auto_output_logging
        self.log_env_details = log_env_details

        # Deactivate git logging in case the user disabled logging code
        if not self.log_code:
            log_git_metadata = False
            log_git_patch = False

        self.log_git_metadata = log_git_metadata
        self.log_git_patch = log_git_patch
        self.log_env_gpu = log_env_gpu
        self.log_env_host = log_env_host
        self.disabled = disabled

        if not self.disabled:
            if len(ALREADY_IMPORTED_MODULES) > 0:
                msg = "You must import Comet before these modules: %s" % ", ".join(
                    ALREADY_IMPORTED_MODULES
                )
                raise ImportError(msg)

        # Generate a unique identifier for this experiment.
        self.id = self._get_experiment_key()

        self.alive = False
        self.is_github = False
        self.focus_link = None
        self.upload_limit = DEFAULT_UPLOAD_SIZE_LIMIT
        self.asset_upload_limit = DEFAULT_ASSET_UPLOAD_SIZE_LIMIT
        self.upload_web_asset_url_prefix = None
        self.upload_web_image_url_prefix = None
        self.upload_api_asset_url_prefix = None
        self.upload_api_image_url_prefix = None

        self.streamer = None
        self.logger = None
        self.gpu_thread = None
        self.run_id = None
        self.project_id = None

        self.main_thread_id = get_ident()

        # If set to True, wrappers should only run the original code
        self.disabled_monkey_patching = False

        # Experiment state
        self.context = None
        self.curr_step = None

        self.figure_counter = 0
        self.batch_report_rate = 10

        self.feature_toggles = {}

        # Storage area for use by loggers
        self._storage = defaultdict(dict)

        self._pending_calls = []

        # Cleanup old experiment before replace it
        if get_global_experiment() is not None and get_global_experiment() is not self:
            get_global_experiment()._on_end(wait=False)

        set_global_experiment(self)

        self.rpc_callbacks = {}

    def clean(self):
        """ Clean the experiment loggers, useful in case you want to debug
        your scripts with IPDB.
        """
        self._on_end(wait=False)

    def end(self):
        """
        Use to indicate that the experiment is complete. Useful in
        Jupyter environments to signal comel.ml that the experiment
        has ended.

        In Jupyter, this will also upload the commands that created
        the experiment, from the beginning to the end of this
        session. See the Code tab at Comet.ml.
        """
        if self._in_jupyter_environment() and self.log_code:
            source_code = self._get_jupyter_source_code()
            self.set_code(source_code)
        self._on_end(wait=True)

    def display(self, clear=False, wait=True, new=0, autoraise=True):
        """
        Show the comet.ml experiment page in an IFrame in a
        Jupyter notebook or Jupyter lab, OR open a browser
        window or tab.

        For Jupyter environments:

        Args:
            clear: to clear the output area, use clear=True
            wait: to wait for the next displayed item, use
                  wait=True (cuts down on flashing)

        For non-Jupyter environments:

        Args:
            new: open a new browser window if new=1, otherwise re-use
                 existing window/tab
            autoraise: make the browser tab/window active
        """
        if self._in_jupyter_environment():
            from IPython.display import display, IFrame, clear_output

            if clear:
                clear_output(wait=wait)
            display(
                IFrame(src=self._get_experiment_url(), width="100%", height="800px")
            )
        else:
            import webbrowser

            webbrowser.open(self._get_experiment_url(), new=new, autoraise=autoraise)

    def _get_experiment_key(self):
        return generate_guid()

    def _on_start(self):
        """ Called when the Experiment is started
        """
        self._mark_as_started()

    def _mark_as_started(self):
        pass

    def _mark_as_ended(self):
        pass

    def _report_summary(self):
        """
        Display to logger a summary of experiment if there
        is anything to report. If not, no summary will be
        shown.
        """
        self._summary["data"]["url"] = self._get_experiment_url()
        topics = [("Data", "data"), ("Metrics", "metric"), ("Other", "other")]
        if sum([value for value in self._summary["uploads"].values()]) > 0:
            topics.append(("Uploads", "uploads"))
        heading_printed = False
        for description, topic in topics:
            section_printed = False
            max_size = 0
            for key in self._summary[topic]:
                max_size = max(len(str(key)), max_size)
            for key in sorted(self._summary[topic]):
                if not heading_printed:
                    LOGGER.info("----------------------------")
                    LOGGER.info("Comet.ml Experiment Summary:")
                    heading_printed = True
                if not section_printed:
                    LOGGER.info("  %s:", description)
                    section_printed = True
                LOGGER.info(
                    "    %" + str(max_size) + "s: %s", key, self._summary[topic][key]
                )
        if heading_printed:
            LOGGER.info("----------------------------")

    def _on_end(self, wait=True):
        """ Called when the Experiment is replaced by another one or at the
        end of the script
        """
        LOGGER.debug("Experiment on_end called, wait %s", wait)
        if self.alive:
            try:
                self._report_summary()
            except Exception:
                LOGGER.debug("Summary not reported", exc_info=True)
        successful_clean = True

        if self.logger is not None:
            LOGGER.debug("Cleaning STDLogger")
            self.logger.clean()

        if self.gpu_thread is not None:
            self.gpu_thread.close()
            if wait is True:
                LOGGER.debug("GPU THREAD before join")
                self.gpu_thread.join(2)
                LOGGER.debug("GPU THREAD after join")

        if self.streamer is not None:
            LOGGER.debug("Closing streamer")
            self.streamer.close()
            if wait is True:
                successful_clean = self.streamer.wait_for_finish()

        self._mark_as_ended()

        # Mark the experiment as not alive anymore to avoid future new
        # messages
        self.alive = False

        return successful_clean

    def _start(self):
        try:
            self.alive = self._setup_streamer()

            if not self.alive:
                LOGGER.debug("Experiment is not alive, exiting")
                return

            # Register the cleaning method to be called when the script ends
            atexit.register(self._on_end)

        except CometException as exception:
            tb = traceback.format_exc()
            default_log_message = "Run will not be logged" + GO_TO_DOCS_MSG

            exc_log_message = getattr(exception, "log_message", None)
            exc_args = getattr(exception, "args", None)
            log_message = None
            if exc_log_message is not None and exc_args is not None:
                try:
                    log_message = exc_log_message % exc_args
                except TypeError:
                    pass

            if log_message is None:
                log_message = default_log_message

            LOGGER.error(log_message, exc_info=True)
            self._report(event_name=EXPERIMENT_CREATION_FAILED, err_msg=tb)
            return None
        except Exception:
            tb = traceback.format_exc()
            err_msg = "Run will not be logged" + GO_TO_DOCS_MSG
            LOGGER.error(err_msg, exc_info=True, extra={"show_traceback": True})
            self._report(event_name=EXPERIMENT_CREATION_FAILED, err_msg=tb)
            return None

        # After the handshake is done, mark the experiment as alive
        self._on_start()

        try:
            self._setup_std_logger()
        except Exception:
            LOGGER.error("Failed to setup the std logger", exc_info=True)

        ##############################################################
        ## log_code:
        ##############################################################
        if self.log_code:
            try:
                filename = self._get_filename()
                self.set_filename(filename)
            except Exception:
                LOGGER.error("Failed to set run file name", exc_info=True)
            try:
                self.set_code(self._get_source_code())
            except Exception:
                LOGGER.error("Failed to set run source code", exc_info=True)

        ##############################################################
        ## log_env_details:
        ##############################################################
        if self.log_env_details:
            try:
                self.set_pip_packages()
            except Exception:
                LOGGER.error("Failed to set run pip packages", exc_info=True)
            try:
                self.set_os_packages()
            except Exception:
                LOGGER.error("Failed to set run os packages", exc_info=True)

            try:
                if self.log_env_host:
                    self._log_env_details()
            except Exception:
                LOGGER.error("Failed to log environment details", exc_info=True)

            try:
                if self.log_env_gpu and is_gpu_details_available():
                    self._start_gpu_thread()
                else:
                    LOGGER.debug("GPU details unavailable, don't start the GPU thread")
            except Exception:
                LOGGER.error("Failed to start the GPU tracking thread", exc_info=True)

            try:
                if self.log_git_metadata:
                    self.set_git_metadata()
            except Exception:
                LOGGER.error("Failed to log git metadata", exc_info=True)

            try:
                if self.log_git_patch:
                    self._upload_git_patch()
            except Exception:
                LOGGER.error("Failed to log git patch", exc_info=True)
                tb = traceback.format_exc()
                self._report(event_name=GIT_PATCH_GENERATION_FAILED, err_msg=tb)
                LOGGER.error("Failed to log git patch", exc_info=True)

        ##############################################################
        ## parse_args:
        ##############################################################
        if self.parse_args:
            try:
                self.set_cmd_args()
            except Exception:
                LOGGER.error("Failed to set run cmd args", exc_info=True)

    def _report(self, *args, **kwargs):
        """ Do nothing, could be overridden by subclasses
        """
        pass

    def _setup_streamer(self):
        """
        Do the necessary work to create mandatory objects, like the streamer
        and feature flags
        """
        raise NotImplementedError()

    def _setup_std_logger(self):
        # Override default sys.stdout and feed to streamer.
        self.logger = get_std_logger(self.auto_output_logging, self.streamer)
        if self.logger is not None:
            self.logger.set_experiment(self)

    def _create_message(self, include_context=True):
        """
        Utility wrapper around the Message() constructor
        Returns: Message() object.

        """
        # First check for pending callbacks call.
        # We do the check in _create_message as it is the most central code
        if get_ident() == self.main_thread_id:
            self._check_rpc_callbacks()

        if include_context is True:
            context = self.context
        else:
            context = None

        return Message(context=context)

    def get_metric(self, name):
        return self.metrics[name]

    def get_parameter(self, name):
        return self.params[name]

    def get_other(self, name):
        return self.others[name]

    def get_key(self):
        """
        Returns the experiment key, useful for using with the ExistingExperiment class
        Returns: Experiment Key (String)
        """
        return self.id

    def log_other(self, key, value):
        """
        Reports key,value to the `Other` tab on Comet.ml. Useful for reporting datasets attributes,
        datasets path, unique identifiers etc.

        See [`log_parameter`](#experimentlog_parameter)

        Args:
            key: Any type of key (str,int,float..)
            value: Any type of value (str,int,float..)

        Returns: None

        """
        if self.alive:
            self._summary["other"][self._summary_name(key)] = value
            message = self._create_message()
            message.set_log_other(key, value)
            self.streamer.put_messge_in_q(message)

        self.others[key] = value

    def _summary_name(self, name):
        """
        If in a context manager, add the context name.
        """
        if self.context is not None:
            return "%s_%s" % (self.context, name)
        else:
            return name

    def log_dependency(self, name, version):
        """
        Reports name,version to the `Installed Packages` tab on Comet.ml. Useful to track dependencies.
        Args:
            name: Any type of key (str,int,float..)
            version: Any type of value (str,int,float..)

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_log_dependency(name, version)
            self.streamer.put_messge_in_q(message)

    def log_system_info(self, key, value):
        """
        Reports key,value to the `System Metric` tab on Comet.ml. Useful to track general system information.
        This information would only show on the table as custom plots are not support for this tab.
        Args:
            key: Any type of key (str,int,float..)
            value: Any type of value (str,int,float..)

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_system_info(key, value)
            self.streamer.put_messge_in_q(message)

    def log_html(self, html, clear=False):
        """
        Reports any HTML blob to the `HTML` tab on Comet.ml. Useful for creating your own rich reports.
        The HTML will be rendered as an Iframe. Inline CSS/JS supported.
        Args:
            html: Any html string. for example:
            clear: Default to False. when setting clear=True it will remove all previous html.
            ```
            experiment.log_html('<a href="www.comet.ml"> I love Comet.ml </a>')
            ```

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            if clear:
                message.set_htmlOverride(html)
            else:
                message.set_html(html)
            self.streamer.put_messge_in_q(message)

    def log_html_url(self, url, text=None, label=None):
        """
        Easy to use method to add a link to a URL in the `HTML` tab
        on comet.ml.

        Args:
            url: a link to a file or notebook, for example
            text: text to use a clickable word or phrase (optional; uses url if not given)
            label: text that preceeds the link

        Examples:

        >>> experiment.log_html_url("https://my-company.com/file.txt")

        Adds html similar to:

        <a href="https://my-company.com/file.txt">https://my-company.com/file.txt</a>

        >>> experiment.log_html_url("https://my-company.com/file.txt", "File")

        Adds html similar to:

        <a href="https://my-company.com/file.txt">File</a>

        >>> experiment.log_html_url("https://my-company.com/file.txt", "File", "Label")

        Adds html similar to:

        Label: <a href="https://my-company.com/file.txt">File</a>

        """
        text = text if text is not None else url
        if label:
            self.log_html(
                """<div><b>%s</b>: <a href="%s" target="_blank">%s</a></div>"""
                % (label, url, text)
            )
        else:
            self.log_html(
                """<div><a href="%s" target="_blank">%s</a></div>""" % (url, text)
            )

    def set_step(self, step):
        """
        Sets the current step in the training process. In Deep Learning each step is after feeding a single batch
         into the network. This is used to generate correct plots on comet.ml. You can also pass the step directly when reporting [log_metric](#experimentlog_metric), and [log_parameter](#experimentlog_parameter).

        Args:
            step: Integer value

        Returns: None

        """

        if step is not None:
            if isinstance(step, numbers.Number):
                self.curr_step = step
                self.log_parameter("curr_step", step)
            else:
                LOGGER.warning(EXPERIMENT_INVALID_STEP, step)

    def log_epoch_end(self, epoch_cnt, step=None):
        """
        Logs that the  epoch finished. required for progress bars.

        Args:
            epoch_cnt: integer

        Returns: None

        """
        self.set_step(step)

        if self.alive:
            self._summary["metric"][self._summary_name("epoch_end")] = epoch_cnt
            if step is not None:
                self._summary["metric"][self._summary_name("step")] = step
            message = self._create_message()
            message.set_param("curr_epoch", epoch_cnt, step=self.curr_step)
            self.streamer.put_messge_in_q(message)

    def log_metric(self, name, value, step=None, include_context=True):
        """
        Logs a general metric (i.e accuracy, f1).

        e.g.
        ```
        y_pred_train = model.predict(X_train)
        acc = compute_accuracy(y_pred_train, y_train)
        experiment.log_metric("accuracy", acc)
        ```

        See also [`log_metrics`](#experimentlog_metrics)


        Args:
            name: String - name of your metric
            value: Float/Integer/Boolean/String
            step: Optional. Used as the X axis when plotting on comet.ml
            include_context: Optional. If set to True (the default), the
                current context will be logged along the metric.

        Returns: None

        Down sampling metrics:
        Comet guarantees to store 15,000 data points for each metric. If more than 15,000 data points are reported we
        perform a form of reservoir sub sampling - https://en.wikipedia.org/wiki/Reservoir_sampling.



        """
        LOGGER.debug("Log metric: %s %r %r", name, value, step)

        self.set_step(step)

        if self.alive:
            message = self._create_message(include_context=include_context)

            if is_list_like(value):
                # Try to get the first value of the Array
                try:
                    if len(value) != 1:
                        raise TypeError()

                    if not isinstance(
                        value[0], (six.integer_types, float, six.string_types, bool)
                    ):
                        raise TypeError()

                    value = value[0]

                except (TypeError):
                    LOGGER.warning(METRIC_ARRAY_WARNING, value)
                    value = str(value)

            self._summary["metric"][self._summary_name(name)] = value
            message.set_metric(name, value, self.curr_step)
            self.streamer.put_messge_in_q(message)

        # save state.
        self.metrics[name] = value

    def log_parameter(self, name, value, step=None):
        """
        Logs a single hyperparameter. For additional values that are not hyper parameters it's encouraged to use [log_other](#experimentlog_other).

        See also [`log_parameters`](#experimentlog_parameters).

        If the same key is reported multiple times only the last reported value will be saved.


        Args:
            name: String - name of your parameter
            value: Float/Integer/Boolean/String/List
            step: Optional. Used as the X axis when plotting on comet.ml

        Returns: None

        """
        self.set_step(step)

        if name in self.params and self.params[name] == value:
            return

        if self.alive:
            message = self._create_message()

            # Check if we have a list-like object or a string
            if is_list_like(value):
                message.set_params(name, value, self.curr_step)
            else:
                message.set_param(name, value, self.curr_step)

            self.streamer.put_messge_in_q(message)

        self.params[name] = value

    def log_figure(self, figure_name=None, figure=None, overwrite=False):
        """
        Logs the global Pyplot figure or the passed one and upload its svg
        version to the backend.

        Args:
            figure_name: Optional. String - name of the figure
            figure: Optional. The figure you want to log. If not set, the global
                pyplot figure will be logged and uploaded
            overwrite: Optional. Boolean - if another figure with the same name
                exists, it will be overwritten if overwrite is set to True.
        """
        if self.alive is False:
            return

        try:
            filename = save_matplotlib_figure(figure)
        except Exception:
            LOGGER.warning("Failing to save the matplotlib figure", exc_info=True)
            # An error occured
            return

        # Pass additional url params
        figure_number = self.figure_counter
        figure_id = generate_guid()
        url_params = {
            "step": self.curr_step,
            "figCounter": figure_number,
            "context": self.context,
            "runId": self.run_id,
            "overwrite": overwrite,
            "imageId": figure_id,
        }

        if figure_name is not None:
            url_params["figName"] = figure_name

        success = self._upload_file_by_path(
            filename,
            "visualization",
            self.upload_limit,
            url_params,
            LOG_FIGURE_TOO_BIG,
            copy_to_tmp=False,
            error_message_identifier=figure_number,
        )

        if not success:
            return

        self._summary["uploads"]["figures"] += 1
        self.figure_counter += 1

        return self._get_uploaded_figure_url(figure_id)

    def log_asset_data(self, data, file_name=None, overwrite=False):
        """
        Logs the data given (str or JSON).

        Args:
            data: data to be saved as asset
            file_name: String - Optional. A custom file name to be displayed
               If not provided the filename from the temporary saved file will be used.
            overwrite: Boolean. Default False. If True will overwrite all existing
               assets with the same name.

        See also: `APIExperiment.get_experiment_asset(return_type="json")`
        """
        try:
            fp = data_to_fp(data)
        except Exception:
            LOGGER.error("Failed to log asset data", exc_info=True)
            return
        if fp is not None:
            return self.log_asset(
                file_data=fp, file_name=file_name, overwrite=overwrite
            )

    def log_asset_folder(self, folder):
        """
        Logs all the files located in the given folder as assets

        Args:
            folder: String - the path to the folder you want to log
        """
        try:
            file_names = sorted(os.listdir(folder))
        except OSError:
            LOGGER.error(LOG_ASSET_FOLDER_ERROR, folder, exc_info=True)
            return

        urls = []

        for file_name in file_names:
            file_path = os.path.join(folder, file_name)

            if os.path.isfile(file_path):
                asset_url = self.log_asset(file_data=file_path)
                urls.append((file_name, asset_url))

        return urls

    def log_asset(
        self,
        file_data=None,  # TODO: REMOVE None when deprecations removed
        file_like_object=None,  # TODO: Deprecated; REMOVE
        file_name=None,
        overwrite=False,
        file_path=None,  # TODO: Deprecated; REMOVE
        copy_to_tmp=True,  # if file_data is a file pointer
    ):
        """
        Logs the Asset determined by file_data.

        Args:
            file_data: String or File-like - either the file path of the file you want
                to log, or a file-like asset.
            file_name: String - Optional. A custom file name to be displayed. If not
                provided the filename from the `file_data` argument will be used.
            overwrite: if True will overwrite all existing assets with the same name.
            copy_to_tmp: If `file_data` is a file-like object, then this flag determines
                if the file is first copied to a temporary file before upload. If
                `copy_to_tmp` is False, then it is sent directly to the cloud.

        Note: Previously you could pass in `file_path` (a path to a file) or
            `file_like_object` (for a file-like object, like a file pointer). That
            form has been deprecated and will be removed completely in a future version.
            Please pass in either the path or a file-like object as `file_data`.

        Examples:

            >>> experiment.log_asset("model1.h5")

            >>> fp = open("model2.h5", "rb")
            >>> experiment.log_asset(fp,
            ...                      file_name="model2.h5")
            >>> fp.close()

            >>> fp = open("model3.h5", "rb")
            >>> experiment.log_asset(fp,
            ...                      file_name="model3.h5",
            ...                      copy_to_tmp=False)
            >>> fp.close()
        """
        if self.alive is False:
            return

        if file_path is not None and file_like_object is not None:
            raise TypeError("log_asset takes a path or file-like-object, not both")

        ## TODO: remove file_path and file_like_object in the future
        if file_like_object is not None:
            LOGGER.info("file_like_object is deprecated; remove named parameter")
            file_data = file_like_object
        elif file_path is not None:
            LOGGER.info("file_path is deprecated; remove named parameter")
            file_data = file_path

        if file_data is None:
            raise TypeError("log_asset requires `file_data`")

        asset_id = generate_guid()
        url_params = {
            "step": self.curr_step,
            "context": self.context,
            "fileName": file_name,
            "runId": self.run_id,
            "overwrite": overwrite,
            "assetId": asset_id,
        }

        isfile = is_valid_file_path(file_data)

        # Detect invalid file paths
        if not isfile and isinstance(file_data, (six.string_types, bytes)):
            LOGGER.error(UPLOAD_FILE_OS_ERROR, file_data)
            return

        if isfile:
            if url_params["fileName"] is None:
                url_params["fileName"] = os.path.basename(file_data)

            success = self._upload_file_by_path(
                file_data,
                "asset",
                self.asset_upload_limit,
                url_params,
                UPLOAD_ASSET_TOO_BIG,
                copy_to_tmp=True,
            )  # copy_to_tmp in order to makes a copy before uploading and removing it

            if not success:
                return
        else:
            success = self._upload_file_like(
                file_data,
                "asset",
                self.asset_upload_limit,
                url_params,
                UPLOAD_ASSET_TOO_BIG,
                copy_to_tmp,
            )

            if not success:
                return

        self._summary["uploads"]["assets"] += 1
        return self._get_uploaded_asset_url(asset_id)

    def _upload_file_by_path(
        self,
        file_path,
        upload_type,
        max_size,
        url_params,
        too_big_log_msg,
        copy_to_tmp,
        error_message_identifier=None,
    ):
        try:
            check_max_file_size(file_path, max_size)
        except FileIsTooBig as exc:
            if error_message_identifier is None:
                error_message_identifier = exc.file_path

            LOGGER.error(
                too_big_log_msg, error_message_identifier, exc.file_size, exc.max_size
            )
            return False
        except Exception:
            LOGGER.debug("Error while checking the file size", exc_info=True)
            return False

        return self._file_upload(
            file_path, upload_type, url_params, copy_to_tmp=copy_to_tmp
        )

    def _upload_file_like(
        self, file_data, upload_type, max_size, url_params, too_big_log_msg, copy_to_tmp
    ):
        if copy_to_tmp:
            # Convert the file-like to a temporary file on disk
            file_path = write_file_like_to_tmp_file(file_data)
            copy_to_tmp = False

            # Todo it would be easier to use the same field name for a file or a figure upload
            if "fileName" in url_params and url_params["fileName"] is None:
                url_params["fileName"] = os.path.basename(file_path)

            if "figName" in url_params and url_params["figName"] is None:
                url_params["figName"] = os.path.basename(file_path)

            return self._upload_file_by_path(
                file_path,
                upload_type,
                max_size,
                url_params,
                too_big_log_msg,
                copy_to_tmp,
            )

        return self._file_upload(
            file_data, upload_type, url_params, copy_to_tmp=copy_to_tmp
        )

    def log_image(
        self,
        image_data=None,  # TODO: REMOVE None when deprecations are removed
        name=None,
        overwrite=False,
        image_format="png",
        image_scale=1.0,
        image_shape=None,
        image_colormap=None,
        image_minmax=None,
        image_channels="last",
        file_path=None,  # TODO: Deprecated; REMOVE
        file_name=None,  # TODO: Deprecated; REMOVE
        copy_to_tmp=True,  # if image_data is a file pointer
    ):
        """
        Logs the image. Images are displayed on the Graphics tab on
        Comet.ml.

        Args:
            image_data: Required. image_data is one of the following:
                - a path (string) to an image
                - a file-like object containing an image
                - a numpy matrix
                - a TensorFlow tensor
                - a PyTorch tensor
                - a list or tuple of values
                - a PIL Image
            name: String - Optional. A custom name to be displayed on the dashboard.
                If not provided the filename from the `image_data` argument will be
                used if it is a path.
            overwrite: Optional. Boolean - If another image with the same name
                exists, it will be overwritten if overwrite is set to True.
            image_format: Optional. String. Default: 'png'. If the image_data is
                actually something that can be turned into an image, this is the
                format used. Typical values include 'png' and 'jpg'.
            image_scale: Optional. Float. Default: 1.0. If the image_data is actually
                something that can be turned into an image, this will be the new
                scale of the image.
            image_shape: Optional. Tuple. Default: None. If the image_data is actually
                something that can be turned into an image, this is the new shape
                of the array. Dimensions are (width, height).
            image_colormap: Optional. String. If the image_data is actually something
                that can be turned into an image, this is the colormap used to
                colorize the matrix.
            image_minmax: Optional. (Number, Number). If the image_data is actually
                something that can be turned into an image, this is the (min, max)
                used to scale the values. Otherwise, the image is autoscaled between
                (array.min, array.max).
            image_channels: Optional. Default 'last'. If the image_data is
                actually something that can be turned into an image, this is the
                setting that indicates where the color information is in the format
                of the 2D data. 'last' indicates that the data is in (rows, columns,
                channels) where 'first' indicates (channels, rows, columns).
            copy_to_tmp: If `image_data` is not a file path, then this flag determines
                if the image is first copied to a temporary file before upload. If
                `copy_to_tmp` is False, then it is sent directly to the cloud.

        NOTE: Previosuly you could pass in `file_name`. Please use `name` now.
        """
        if self.alive is False:
            return

        if file_path is not None:
            LOGGER.info("`file_path` is deprecated; use `file_data`")
            image_data = file_path

        if file_name is not None:
            LOGGER.info("`file_name` is deprecated; use `name`")
            name = file_name

        if image_data is None:
            raise TypeError("log_image requires an image_data")

        # Prepare parameters
        figure_number = self.figure_counter

        image_id = generate_guid()
        url_params = {
            "step": self.curr_step,
            "context": self.context,
            "runId": self.run_id,
            "figName": name,
            "figCounter": figure_number,
            "overwrite": overwrite,
            "imageId": image_id,
        }

        isfile = is_valid_file_path(image_data)

        # Detect invalid file paths
        if not isfile and isinstance(image_data, (six.string_types, bytes)):
            LOGGER.error(UPLOAD_FILE_OS_ERROR, image_data)
            return

        if isfile:
            # Take the filename as a figure name if it wasn't provided, here
            # we know that image_data is a valid file_path
            if url_params["figName"] is None:
                url_params["figName"] = os.path.basename(image_data)

            success = self._upload_file_by_path(
                image_data,
                "visualization",
                self.upload_limit,
                url_params,
                LOG_IMAGE_TOO_BIG,
                copy_to_tmp=copy_to_tmp,
            )

            if not success:
                return
        else:
            try:
                image_object = image_data_to_file_like_object(
                    image_data,
                    name,
                    image_format,
                    image_scale,
                    image_shape,
                    image_colormap,
                    image_minmax,
                    image_channels,
                )
            except Exception:
                LOGGER.error(
                    "Could not convert image_data into an image; ignored", exc_info=True
                )
                return

            success = self._upload_file_like(
                image_object,
                "visualization",
                self.upload_limit,
                url_params,
                LOG_IMAGE_TOO_BIG,
                copy_to_tmp=copy_to_tmp,
            )

            if not success:
                return

        self._summary["uploads"]["images"] += 1
        self.figure_counter += 1

        return self._get_uploaded_image_url(image_id)

    def log_current_epoch(self, value):
        """
        Deprecated.
        """
        if self.alive:
            self._summary["metric"][self._summary_name("curr_epoch")] = value
            message = self._create_message()
            message.set_metric("curr_epoch", value)
            self.streamer.put_messge_in_q(message)

    def log_multiple_params(self, dic, prefix=None, step=None):
        """
        Deprecated. Use log_parameters() instead.
        """
        LOGGER.warning(
            "Experiment.log_multiple_params() has been deprecated and will be removed after 2019/2/1. "
            "Use Experiment.log_parameters() instead"
        )
        self.log_parameters(dic, prefix=prefix, step=step)

    def log_parameters(self, dic, prefix=None, step=None):
        """
        Logs a dictionary of multiple parameters.
        See also [log_parameter](#experimentlog_parameter).

        e.g:
        ```
        experiment = Experiment(api_key="MY_API_KEY")
        params = {
            "batch_size":64,
            "layer1":"LSTM(128)",
            "layer2":"LSTM(128)",
            "MAX_LEN":200
        }

        experiment.log_parameters(params)
        ```

        If you call this method multiple times with the same
        keys your values would be overwritten.  For example:

        ```
        experiment.log_parameters({"key1":"value1","key2":"value2"})
        ```
        On Comet.ml you will see the pairs of key1 and key2.

        If you then call:
        ```
        experiment.log_parameters({"key1":"other value"})l
        ```
        On the UI you will see the pairs key1: other value, key2: value2


        """
        self.set_step(step)

        if self.alive:
            for k in sorted(dic):
                if prefix is not None:
                    self.log_parameter(prefix + "_" + str(k), dic[k], self.curr_step)
                else:
                    self.log_parameter(k, dic[k], self.curr_step)

    def log_multiple_metrics(self, dic, prefix=None, step=None):
        """
        Deprecated. Use log_metrics() instead.
        """
        LOGGER.warning(
            "Experiment.log_multiple_metrics() has been deprecated and will be removed after 2019/2/1. "
            "Use Experiment.log_metrics() instead"
        )
        self.log_metrics(dic, prefix=prefix, step=step)

    def log_metrics(self, dic, prefix=None, step=None):
        """
        Logs a key,value dictionary of metrics.
        See also [`log_metric`](#experimentlog_metric)
        """
        self.set_step(step)

        if self.alive:
            for k in sorted(dic):
                if prefix is not None:
                    self.log_metric(prefix + "_" + str(k), dic[k], self.curr_step)
                else:
                    self.log_metric(k, dic[k], self.curr_step)

    def log_dataset_info(self, name=None, version=None, path=None):
        """
        Used to log information about your dataset.

        Args:
            name: Optional string representing the name of the dataset.
            version: Optional string representing a version identifier.
            path: Optional string that represents the path to the dataset.
                Potential values could be a file system path, S3 path
                or Database query.

        At least one argument should be included. The logged values will
        show on the `Other` tab.
        """
        if name is None and version is None and path is None:
            LOGGER.warning(
                "log_dataset_info: name, version, and path can't all be None"
            )
            return
        info = ""
        if name is not None:
            info += str(name)
        if version is not None:
            if info:
                info += "-"
            info += str(version)
        if path is not None:
            if info:
                info += ", "
            info += str(path)
        self.log_other("dataset_info", info)

    def log_dataset_hash(self, data):
        """
        Used to log the hash of the provided object. This is a best-effort hash computation which is based on the md5
        hash of the underlying string representation of the object data. Developers are encouraged to implement their
        own hash computation that's tailored to their underlying data source. That could be reported as
        `experiment.log_parameter("dataset_hash",your_hash).

        data: Any object that when casted to string (e.g str(data)) returns a value that represents the underlying data.

        """
        try:
            import hashlib

            data_hash = hashlib.md5(str(data).encode("utf-8")).hexdigest()
            self.log_parameter("dataset_hash", data_hash[:12])
        except Exception:
            LOGGER.warning(LOG_DATASET_ERROR, exc_info=True)

    def set_code(self, code):
        """
        Sets the current experiment script's code. Should be called once per experiment.
        Args:
            code: String. Experiment source code.
        """
        if self.alive and code is not None:
            message = self._create_message()
            message.set_code(code)
            self.streamer.put_messge_in_q(message)

    def set_model_graph(self, graph):
        """
        Sets the current experiment computation graph.
        Args:
            graph: String or Google Tensorflow Graph Format.
        """
        if self.alive:

            LOGGER.debug("Set model graph called")

            if type(graph).__name__ == "Graph":  # Tensorflow Graph Definition
                from google.protobuf import json_format

                graph_def = graph.as_graph_def()
                graph = json_format.MessageToJson(graph_def)

            message = self._create_message()
            message.set_graph(graph)
            self.streamer.put_messge_in_q(message)

    def set_filename(self, fname):
        """
        Sets the current experiment filename.
        Args:
            fname: String. script's filename.
        """
        self.filename = fname
        if self.alive:
            message = self._create_message()
            message.set_filename(fname)
            self.streamer.put_messge_in_q(message)

    def set_name(self, name):
        """
        Set a name for the experiment. Useful for filtering and searching on Comet.ml.
        Will shown by default under the `Other` tab.
        Args:
            name: String. A name for the experiment.
        """
        self.log_other("Name", name)

    def set_os_packages(self):
        """
        Reads the installed os packages and reports them to server
        as a message.
        Returns: None

        """
        if self.alive:
            try:
                os_packages_list = read_unix_packages()
                if os_packages_list is not None:
                    message = self._create_message()
                    message.set_os_packages(os_packages_list)
                    self.streamer.put_messge_in_q(message)
            except Exception:
                LOGGER.warning(
                    "Failing to collect the installed os packages", exc_info=True
                )

    def set_pip_packages(self):
        """
        Reads the installed pip packages using pip's CLI and reports them to server as a message.
        Returns: None

        """
        if self.alive:
            try:
                import pkg_resources

                installed_packages = [d for d in pkg_resources.working_set]
                installed_packages_list = sorted(
                    ["%s==%s" % (i.key, i.version) for i in installed_packages]
                )
                message = self._create_message()
                message.set_installed_packages(installed_packages_list)
                self.streamer.put_messge_in_q(message)
            except Exception:
                LOGGER.warning(
                    "Failing to collect the installed pip packages", exc_info=True
                )

    def set_cmd_args(self):
        if self.alive:
            args = get_cmd_args_dict()
            LOGGER.debug("Command line arguments %r", args)
            if args is not None:
                for k, v in args.items():
                    self.log_parameter(k, v)

    # Context context-managers

    @contextmanager
    def train(self):
        """
        A context manager to mark the beginning and the end of the training
        phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        experiment = Experiment(api_key="MY_API_KEY")
        with experiment.train():
            model.fit(x_train, y_train)
            accuracy = compute_accuracy(model.predict(x_train),y_train) # returns the train accuracy
            experiment.log_metric("accuracy",accuracy) # this will be logged as train accuracy based on the context.
        ```

        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "train"

        yield self

        # Restore the old one
        self.context = old_context

    @contextmanager
    def validate(self):
        """
        A context manager to mark the beginning and the end of the validating
        phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        with experiment.validate():
            pred = model.predict(x_validation)
            val_acc = compute_accuracy(pred, y_validation)
            experiment.log_metric("accuracy", val_acc) # this will be logged as validation accuracy based on the context.
        ```


        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "validate"

        yield self

        # Restore the old one
        self.context = old_context

    @contextmanager
    def test(self):
        """
        A context manager to mark the beginning and the end of the testing phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        with experiment.test():
            pred = model.predict(x_test)
            test_acc = compute_accuracy(pred, y_test)
            experiment.log_metric("accuracy", test_acc) # this will be logged as test accuracy based on the context.
        ```

        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "test"

        yield self

        # Restore the old one
        self.context = old_context

    def get_keras_callback(self):
        """
        Returns an instance of Comet.ml's Keras callback. This callback is already added to your Keras `model.fit()` callbacks list automatically, to report model training metrics to Comet.ml.


        e.g:
        ```
        experiment = Experiment(api_key="MY_API_KEY")
        comet_callback = experiment.get_keras_callback()
        ```

        Returns: Comet.ml Keras callback.

        """
        if self.alive:
            from comet_ml.frameworks import KerasCallback

            return KerasCallback(
                self,
                log_params=self.auto_param_logging,
                log_metrics=self.auto_metric_logging,
                log_graph=self.log_graph,
            )

        from comet_ml.frameworks import EmptyKerasCallback

        return EmptyKerasCallback()

    def disable_mp(self):
        """ Disabling the auto-collection of metrics and monkey-patching of
        the Machine Learning frameworks.
        """
        self.disabled_monkey_patching = True

    def register_callback(self, function):
        """
        Register the function passed as argument to be a RPC.
        Args:
            function: Callable.
        """
        function_name = function.__name__

        if isinstance(function, types.LambdaType) and function_name == "<lambda>":
            raise LambdaUnsupported()

        if function_name in self.rpc_callbacks:
            raise RPCFunctionAlreadyRegistered(function_name)

        self.rpc_callbacks[function_name] = function

    def unregister_callback(self, function):
        """
        Unregister the function passed as argument.
        Args:
            function: Callable.
        """
        function_name = function.__name__

        self.rpc_callbacks.pop(function_name, None)

    def _get_jupyter_source_code(self):
        """
        Get the Jupyter source code from the history. Assumes that this
        method is run in a jupyter environment.

        Returns the command-history as a string that lead to this point.
        """

        def in_format(n):
            return "_i%s" % n

        import IPython

        ipy = IPython.get_ipython()
        source = io.StringIO()
        n = 1
        while in_format(n) in ipy.ns_table["user_local"]:
            source.write("# %%%% In [%s]:\n" % n)
            source.write(ipy.ns_table["user_local"][in_format(n)])
            source.write("\n\n")
            n += 1
        return source.getvalue()

    def _get_source_code(self):
        """Inspects the stack to detect calling script. Reads source code
        from disk and logs it.
        """
        if self._in_jupyter_environment():
            return None  # upload it with experiment.end()
        else:
            for frame in inspect.stack(context=1):
                module = inspect.getmodule(frame[0])
                if module is not None:
                    if not module.__name__.startswith("comet_ml"):
                        filename = module.__file__.rstrip("cd")
                        with open(filename) as f:
                            return f.read()
                else:
                    return None  # perhaps in ipython interactive
        LOGGER.warning("Failed to find source code module")

    def _in_jupyter_environment(self):
        """
        Check to see if code is running in a Jupyter environment,
        including jupyter notebook, lab, or console.
        """
        try:
            import IPython
        except Exception:
            return False

        ipy = IPython.get_ipython()
        if ipy is None or not hasattr(ipy, "kernel"):
            return False
        else:
            return True

    def _in_ipython_environment(self):
        """
        Check to see if code is running in an IPython environment.
        """
        try:
            import IPython
        except Exception:
            return False

        ipy = IPython.get_ipython()
        if ipy is None:
            return False
        else:
            return True

    def _get_filename(self):
        """
        Get the filename of the executing code, if possible.
        """
        if self._in_jupyter_environment():
            return "Jupyter interactive"
        elif sys.argv:
            pathname = os.path.dirname(sys.argv[0])
            abs_path = os.path.abspath(pathname)
            filename = os.path.basename(sys.argv[0])
            full_path = os.path.join(abs_path, filename)
            return full_path

        return None

    def set_git_metadata(self):
        if self.alive:
            current_path = os.getcwd()

            git_metadata = get_git_metadata(current_path)

            if git_metadata:
                message = self._create_message()
                message.set_git_metadata(git_metadata)
                self.streamer.put_messge_in_q(message)

    def _upload_git_patch(self):
        if not self.alive:
            return

        current_path = os.getcwd()
        git_patch = find_git_patch(current_path)
        if not git_patch:
            LOGGER.debug("Git patch is empty, nothing to upload")
            return

        archive, zip_path = compress_git_patch(git_patch)
        self._file_upload(zip_path, "git-patch", clean=True)
        LOGGER.debug("Git patch upload launched")

    def _log_env_details(self):
        if self.alive:
            message = self._create_message()
            message.set_env_details(get_env_details())
            self.streamer.put_messge_in_q(message)

    def _get_optimization_id_for_api_key(self, api_key):
        global_optimizer = get_global_optimizer()
        if global_optimizer is not None:
            if global_optimizer.api_key == api_key:
                return global_optimizer.id

            else:
                LOGGER.warning(EXPERIMENT_OPTIMIZER_API_KEY_MISMTACH_WARNING)
        return None

    def _start_gpu_thread(self):
        if not self.alive:
            return

        # First sends the static info as a message
        gpu_static_info = get_gpu_static_info()
        message = self._create_message()
        message.set_gpu_static_info(gpu_static_info)
        self.streamer.put_messge_in_q(message)

        # Them sends the one-time metrics
        one_time_gpu_metrics = get_initial_gpu_metric()
        metrics = convert_gpu_details_to_metrics(one_time_gpu_metrics)
        for metric in metrics:
            self.log_metric(metric["name"], metric["value"])

        # Now starts the thread that will be called recurrently
        self.gpu_thread = GPULoggingThread(
            DEFAULT_GPU_MONITOR_INTERVAL, self._log_gpu_details
        )
        self.gpu_thread.start()

        # Connect the streamer and the gpu thread
        self.streamer.on_gpu_monitor_interval = self.gpu_thread.update_internal

    def _log_gpu_details(self, gpu_details):
        metrics = convert_gpu_details_to_metrics(gpu_details)
        for metric in metrics:
            self.log_metric(metric["name"], metric["value"], include_context=False)

    def _file_upload(
        self, upload_file, upload_type, url_params=None, copy_to_tmp=False, clean=None
    ):
        # If we cannot remove the uploaded file or need the file content will
        # be frozen to the time the upload call is made, pass copy_to_tmp with
        # True value
        if copy_to_tmp is True:
            tmpfile = tempfile.NamedTemporaryFile(delete=False)
            shutil.copyfile(upload_file, tmpfile.name)
            upload_file = tmpfile.name
            if clean is None:
                # Clean the temporary file after upload
                clean = True
        else:
            if clean is None:
                # Don't risk cleaning an existing file
                clean = False

        upload_message = UploadFileMessage(
            upload_file, upload_type, url_params, clean=clean
        )
        self.streamer.put_messge_in_q(upload_message)

        return True  # The upload was successful

    def _get_uploaded_asset_url(self, asset_id):
        web_url = format_url(
            self.upload_web_asset_url_prefix, assetId=asset_id, experimentKey=self.id
        )
        api_url = format_url(
            self.upload_api_asset_url_prefix, assetId=asset_id, experimentKey=self.id
        )
        return {"web": web_url, "api": api_url}

    def _get_uploaded_image_url(self, image_id):
        web_url = format_url(
            self.upload_web_image_url_prefix, imageId=image_id, experimentKey=self.id
        )
        api_url = format_url(
            self.upload_api_image_url_prefix, imageId=image_id, experimentKey=self.id
        )
        return {"web": web_url, "api": api_url}

    def _get_uploaded_figure_url(self, figure_id):
        web_url = format_url(
            self.upload_web_image_url_prefix, imageId=figure_id, experimentKey=self.id
        )
        api_url = format_url(
            self.upload_api_image_url_prefix, imageId=figure_id, experimentKey=self.id
        )
        return {"web": web_url, "api": api_url}

    def _add_pending_call(self, rpc_call):
        self._pending_calls.append(rpc_call)

    def _check_rpc_callbacks(self):
        while len(self._pending_calls) > 0:
            call = self._pending_calls.pop()
            if call is not None:
                try:
                    self._call_rpc_callback(call)
                except Exception:
                    LOGGER.debug("Failed to call rpc %r", call, exc_info=True)

    def _call_rpc_callback(self, rpc_call):
        if rpc_call.cometDefined is False:
            function_name = rpc_call.functionName

            start_time = local_timestamp()

            try:
                function = self.rpc_callbacks[function_name]
                remote_call_result = call_remote_function(function, self, rpc_call)
            except KeyError:
                error = "Unregistered remote action %r" % function_name
                remote_call_result = {"success": False, "error": error}

            end_time = local_timestamp()

            # Send the result to the backend
            self.connection.send_rpc_result(
                rpc_call.callId, remote_call_result, start_time, end_time
            )

            return

        # Hardcoded internal callbacks
        if rpc_call.functionName == "stop":
            raise InterruptedExperiment(rpc_call.userName)
        else:
            raise NotImplementedError()

    def add_tag(self, tag):
        """
        Add a tag to the experiment. Tags will be shown in the dashboard.
        Args:
            tag: String. A tag to add to the experiment.
        """
        try:
            self.tags.add(tag)
            return True
        except Exception:
            LOGGER.warning(ADD_TAGS_ERROR, tag, exc_info=True)
            return False

    def add_tags(self, tags):
        """
        Add several tags to the experiment. Tags will be shown in the
        dashboard.
        Args:
            tag: List<String>. Tags list to add to the experiment.
        """
        try:
            self.tags = self.tags.union(tags)
            return True
        except Exception:
            LOGGER.warning(ADD_TAGS_ERROR, tags, exc_info=True)
            return False

    def get_tags(self):
        """
        Return the tags of this experiment.
        Returns: set<String>. The set of tags.
        """
        return list(self.tags)
