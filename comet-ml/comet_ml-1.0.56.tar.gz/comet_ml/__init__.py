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

"""comet-ml"""
from __future__ import print_function

import logging
import time
import traceback

import requests
import six
from pkg_resources import DistributionNotFound, get_distribution

from ._logging import (
    EXPERIMENT_LIVE,
    INTERNET_CONNECTION_ERROR,
    INVALID_API_KEY,
    PARSING_ERR_MSG,
    ADD_TAGS_ERROR,
    setup,
    setup_http_handler,
    REGISTER_RPC_FAILED,
    ADD_SYMLINK_ERROR,
)
from ._reporting import EXPERIMENT_CREATED, EXPERIMENT_CREATION_FAILED
from .api import API
from .comet import (
    Streamer,
    generate_guid,
    get_api_key,
    is_valid_guid,
    get_ws_url,
    get_previous_experiment,
    format_url,
)
from .config import get_config, get_global_experiment, set_global_optimizer
from .connection import (
    log_url,
    OptimizerConnection,
    get_optimizer_address,
    get_backend_address,
    RestServerConnection,
    WebSocketConnection,
    INITIAL_BEAT_DURATION,
)
from .exceptions import (
    AuthenticationError,
    InvalidAPIKey,
    NoMoreSuggestionsAvailable,
    NotParametrizedException,
    OptimizationMultipleParams,
    PCSParsingError,
    PCSCastingError,
    ValidationError,
    BadCallbackArguments,
)
from .rpc import create_remote_call
from .experiment import BaseExperiment
from .feature_toggles import FeatureToggles, HTTP_LOGGING
from .keras_logger import patch as keras_patch
from .monkey_patching import CometModuleFinder
from .optimization import Suggestion, parse_pcs
from .sklearn_logger import patch as sklearn_patch
from .tensorboard_logger import patch as tb_patch
from .tensorflow_logger import patch as tf_patch
from .pytorch_logger import patch as pytorch_patch
from .fastai_logger import patch as fastai_patch
from .rpc import get_remote_action_definition
from .offline import OfflineExperiment

try:
    __version__ = get_distribution("comet_ml").version
except DistributionNotFound:
    __version__ = "Please install comet with `pip install comet_ml`"

__author__ = "Gideon<Gideon@comet.ml>"
__all__ = ["Experiment"]

LOGGER = logging.getLogger(__name__)

if not get_config("comet.disable_auto_logging"):
    # Activate the monkey patching
    MODULE_FINDER = CometModuleFinder()
    keras_patch(MODULE_FINDER)
    sklearn_patch(MODULE_FINDER)
    tf_patch(MODULE_FINDER)
    tb_patch(MODULE_FINDER)
    pytorch_patch(MODULE_FINDER)
    fastai_patch(MODULE_FINDER)
    MODULE_FINDER.start()

# Configure the logging
setup(get_config())


def start():
    """
    If you are not using an Experiment in your first loaded Python file, you
    must import `comet_ml` and call `comet_ml.start` before any other imports
    to ensure that comet.ml is initialized correctly.
    """


__all__ = ["API", "OfflineExperiment", "Experiment", "ExistingExperiment", "Optimizer"]


class Experiment(BaseExperiment):
    """
    Experiment is a unit of measurable research that defines a single run with some data/parameters/code/results.

    Creating an Experiment object in your code will report a new experiment to your Comet.ml project. Your Experiment
    will automatically track and collect many things and will also allow you to manually report anything.

    You can create multiple objects in one script (such as when looping over multiple hyper parameters).

    """

    def __init__(
        self,
        api_key=None,
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
            api_key: Your API key obtained from comet.ml
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

        self.api_key = get_api_key(api_key, self.config)

        if self.api_key is None:
            raise ValueError(
                "Comet.ml requires an API key. Please provide as the "
                "first argument to Experiment(api_key) or as an environment"
                " variable named COMET_API_KEY "
            )

        self.optimization_id = self._get_optimization_id_for_api_key(self.api_key)

        super(Experiment, self).__init__(
            project_name=project_name,
            team_name=team_name,
            workspace=workspace,
            log_code=log_code,
            log_graph=log_graph,
            auto_param_logging=auto_param_logging,
            auto_metric_logging=auto_metric_logging,
            parse_args=parse_args,
            auto_output_logging=auto_output_logging,
            log_env_details=log_env_details,
            log_git_metadata=log_git_metadata,
            log_git_patch=log_git_patch,
            disabled=disabled,
            log_env_gpu=log_env_gpu,
            log_env_host=log_env_host,
        )

        self.ws_connection = None
        self.connection = None

        if disabled is not True:
            self._start()

            if self.alive is True:
                self._report(event_name=EXPERIMENT_CREATED)

                LOGGER.info(EXPERIMENT_LIVE, self._get_experiment_url())

    def _setup_http_handler(self):
        if not self.feature_toggles[HTTP_LOGGING]:
            LOGGER.debug("Do not setup http logger, disabled by feature toggle")
            return

        self.http_handler = setup_http_handler(
            log_url(get_backend_address()), self.api_key, self.id
        )

    def _setup_streamer(self):
        """
        Do the necessary work to create mandatory objects, like the streamer
        and feature flags
        """

        server_address = get_backend_address()

        self.connection = RestServerConnection(
            self.api_key, self.id, self.optimization_id, server_address
        )

        try:
            ws_server_from_backend, initial_offset = self._authenticate()
        except ValueError:
            tb = traceback.format_exc()
            LOGGER.error(INTERNET_CONNECTION_ERROR, exc_info=True)
            self._report(event_name=EXPERIMENT_CREATION_FAILED, err_msg=tb)
            return False

        # Authentication failed somehow
        if ws_server_from_backend is None:
            return False

        ws_server = get_ws_url(ws_server_from_backend, self.config)

        # Generate the full ws url based on ws server
        full_ws_url = format_url(ws_server, apiKey=self.api_key, runId=self.run_id)

        # Setup the HTTP handler
        self._setup_http_handler()

        # Initiate the streamer
        self._initialize_streamer(full_ws_url, initial_offset)

        return True

    def _authenticate(self):
        """
        Do the handshake with the Backend to authenticate the api key and get
        various parameters and settings
        """
        # Get an id for this run
        run_id_results = self.connection.get_run_id(self.project_name, self.workspace)

        (
            self.run_id,
            ws_server,
            self.project_id,
            self.is_github,
            self.focus_link,
            self.upload_limit,
            feature_toggles,
            initial_offset,
            self.upload_web_asset_url_prefix,
            self.upload_web_image_url_prefix,
            self.upload_api_asset_url_prefix,
            self.upload_api_image_url_prefix,
        ) = run_id_results

        self.feature_toggles = FeatureToggles(feature_toggles, self.config)

        return (ws_server, initial_offset)

    def _initialize_streamer(self, full_ws_url, initial_offset):
        """
        Initialize the streamer with the websocket url received during the
        handshake.
        """
        # Initiate the streamer
        self.ws_connection = WebSocketConnection(full_ws_url, self.connection)
        self.ws_connection.start()
        self.ws_connection.wait_for_connection()
        self.streamer = Streamer(
            self.ws_connection,
            INITIAL_BEAT_DURATION,
            self.connection,
            initial_offset,
            self.id,
            self.api_key,
            self.run_id,
            self.project_id,
            self.optimization_id,
            self._on_pending_rpcs_callback,
            self.config["comet.timeout.cleaning"],
            self.config["comet.timeout.upload"],
        )

        # Start streamer thread.
        self.streamer.start()

    def _mark_as_started(self):
        try:
            self.connection.update_experiment_status(
                self.run_id, self.project_id, self.alive
            )
        except Exception:
            LOGGER.error("Failed to report experiment status", exc_info=True)

    def _mark_as_ended(self):
        if self.alive:
            try:
                self.connection.update_experiment_status(
                    self.run_id, self.project_id, False
                )
            except Exception:
                LOGGER.error("Failed to report experiment status", exc_info=True)

    def _report(self, *args, **kwargs):
        self.connection.report(*args, **kwargs)

    def _on_end(self, wait=True):
        """ Called when the Experiment is replaced by another one or at the
        end of the script
        """
        successful_clean = super(Experiment, self)._on_end(wait=wait)

        if not successful_clean:
            LOGGER.warning("Failed to log run in comet.ml")
        else:
            if self.alive:
                LOGGER.info(EXPERIMENT_LIVE, self._get_experiment_url())

            if self.ws_connection is not None:
                self.ws_connection.close()
                LOGGER.debug("Waiting for WS connection to close")
                if wait is True:
                    self.ws_connection.wait_for_finish()

            if self.connection is not None:
                self.connection.close()

    def _get_experiment_url(self):
        if self.focus_link:
            return self.focus_link + self.id

        return ""

    def _on_pending_rpcs_callback(self):
        """ Called by streamer when we have pending rpcs
        """
        LOGGER.debug("Checking pending rpcs")
        calls = self.connection.get_pending_rpcs()["remoteProcedureCalls"]

        LOGGER.debug("Got pending rpcs: %r", calls)
        for raw_call in calls:
            call = create_remote_call(raw_call)
            if call is None:
                continue
            self._add_pending_call(call)

    def create_symlink(self, project_name):
        """
        creates a symlink for this experiment in another project.
        The experiment will now be displayed in the project provided and the original project.

        Args:
            project_name: String. represents the project name. Project must exists.
        """
        try:
            if self.alive:
                self.connection.send_new_symlink(project_name)
        except Exception:
            LOGGER.warning(ADD_SYMLINK_ERROR, project_name, exc_info=True)

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
                IFrame(
                    src=get_global_experiment()._get_experiment_url(),
                    width="100%",
                    height="800px",
                )
            )
        else:
            import webbrowser

            webbrowser.open(
                get_global_experiment()._get_experiment_url(),
                new=new,
                autoraise=autoraise,
            )

    def add_tag(self, tag):
        """
        Add a tag to the experiment. Tags will be shown in the dashboard.
        Args:
            tag: String. A tag to add to the experiment.
        """
        try:
            if self.alive:
                self.connection.add_tags([tag])

            super(Experiment, self).add_tag(tag)
        except Exception:
            LOGGER.warning(ADD_TAGS_ERROR, tag, exc_info=True)

    def add_tags(self, tags):
        """
        Add several tags to the experiment. Tags will be shown in the
        dashboard.
        Args:
            tag: List<String>. Tags list to add to the experiment.
        """
        try:
            if self.alive:
                self.connection.add_tags(tags)

            # If we successfully send them to the backend, save them locally
            super(Experiment, self).add_tags(tags)
        except Exception:
            LOGGER.warning(ADD_TAGS_ERROR, tags, exc_info=True)

    def register_callback(self, remote_action):
        """
        Register the remote_action passed as argument to be a RPC.
        Args:
            remote_action: Callable.
        """
        super(Experiment, self).register_callback(remote_action)

        try:
            remote_action_definition = get_remote_action_definition(remote_action)
        except BadCallbackArguments as exc:
            # Don't keep bad callbacks registered
            self.unregister_callback(remote_action)
            LOGGER.warning(str(exc), exc_info=True)
            return

        try:
            self._register_callback_remotely(remote_action_definition)
        except Exception:
            # Don't keep bad callbacks registered
            self.unregister_callback(remote_action)
            LOGGER.warning(
                REGISTER_RPC_FAILED, remote_action_definition["functionName"]
            )

    def _register_callback_remotely(self, remote_action_definition):
        self.connection.register_rpc(remote_action_definition)


class ExistingExperiment(Experiment):
    """Existing Experiment allows you to report information to an
    experiment that already exists on comet.ml and is not currently
    running. This is useful when your training and testing happen on
    different scripts.

    For example:

    train.py:
    ```
    exp = Experiment(api_key="my-key")
    score = train_model()
    exp.log_metric("train accuracy", score)
    ```

    Now obtain the experiment key from comet.ml. If it's not visible
    on your experiment table you can click `Customize` and add it as a
    column.


    test.py:
    ```
    exp = ExistingExperiment(api_key="my-key",
             previous_experiment="your experiment key from comet.ml")
    score = test_model()
    exp.log_metric("test accuracy", score)
    ```

    Alternatively, you can pass the api_key via an environment
    variable named `COMET_API_KEY` and the previous experiment id via
    an environment variable named `COMET_EXPERIMENT_KEY` and omit them
    from the ExistingExperiment constructor:

    ```
    exp = ExistingExperiment()
    score = test_model()
    exp.log_metric("test accuracy", score)
    ```

    """

    def __init__(self, api_key=None, previous_experiment=None, **kwargs):
        """
        Creates a new experiment on the Comet.ml frontend.
        Args:
            api_key: Your API key obtained from comet.ml
            previous_experiment: Your experiment key from comet.ml
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
        # Validate the previous experiment id
        self.config = get_config()

        self.previous_experiment = get_previous_experiment(
            previous_experiment, self.config
        )

        if not is_valid_guid(self.previous_experiment):
            raise ValueError("Invalid experiment key: %s" % self.previous_experiment)

        self.step_copy = kwargs.pop("step_copy", None)

        ## Defaults for ExistingExperiment:
        ## For now, don't destroy previous Experiment information by default:
        for key in [
            "log_code",
            "log_graph",
            "parse_args",
            "log_env_details",
            "log_git_metadata",
            "log_git_patch",
            "log_env_gpu",
            "log_env_host",
        ]:
            if key not in kwargs:
                kwargs[key] = False
        super(ExistingExperiment, self).__init__(api_key, **kwargs)

    def _get_experiment_key(self):
        if self.step_copy is None:
            return self.previous_experiment
        else:
            return generate_guid()

    def _authenticate(self):
        """
        Do the handshake with the Backend to authenticate the api key and get
        various parameters and settings
        """
        # Get an id for this run
        try:
            if self.step_copy is None:
                run_id_response = self.connection.get_old_run_id(
                    self.previous_experiment
                )
            else:
                run_id_response = self.connection.copy_run(
                    self.previous_experiment, self.step_copy
                )

            (
                self.run_id,
                full_ws_url,
                self.project_id,
                self.is_github,
                self.focus_link,
                self.upload_limit,
                feature_toggles,
                initial_offset,
                self.upload_web_asset_url_prefix,
                self.upload_web_image_url_prefix,
                self.upload_api_asset_url_prefix,
                self.upload_api_image_url_prefix,
            ) = run_id_response

            self.feature_toggles = FeatureToggles(feature_toggles, self.config)

            return (full_ws_url, initial_offset)

        except InvalidAPIKey as e:
            LOGGER.error(INVALID_API_KEY, e.api_key, exc_info=True)
            return

        except ValueError:
            LOGGER.error(INTERNET_CONNECTION_ERROR, exc_info=True)
            return

    def _create_message(self, include_context=True):
        return super(ExistingExperiment, self)._create_message(include_context)


class Optimizer(object):
    '''
    An Optimizer is the object that you can use to dynamically optimize your hyper-parameters on the cloud.

    You can use it this way:

    ```
    optimizer = Optimizer("API_KEY")

    # Declare your hyper-parameters in the PCS format
    params = """
    x integer [1, 10] [10]
    y real [1, 10] [1.0]
    """

    optimizer.set_params(params)

    # get_suggestion will raise when no new suggestion is available
    while True:
        # Get a suggestion
        suggestion = optimizer.get_suggestion()

        # Create a new experiment associated with the Optimizer
        experiment = Experiment("API_KEY")

        # Test the model
        score = fit(suggestion["x"])

        # Report the score back
        suggestion.report_score("accuracy",score)
    ```

    '''

    def __init__(self, api_key=None):
        """
        Creates an Optimizer that you can use to get hyper-parameter
        suggestions.

        Args:
            api_key: Your API key obtained from comet.ml
        """
        self.config = get_config()
        self.api_key = get_api_key(api_key, self.config)
        self.id = generate_guid()
        self.headers = {"OPTIMIZATION-ID": self.id}
        self.types = {}
        self.params_set = False
        optimizer_address = get_optimizer_address(self.config)
        self.connection = OptimizerConnection(self.headers, optimizer_address)

        self._authenticate()

        # Save the optimization id in global config so Experiment can use it.
        set_global_optimizer(self)

    def _authenticate(self):
        # Authenticate to the hyper-parameter service
        try:
            self.connection.authenticate(self.api_key, self.id)
        except requests.exceptions.HTTPError as e:
            response = e.response
            # If their was a validation error, print it
            if response.status_code == 400:
                try:
                    data = response.json()
                    error = data.get("msg")
                    if error:
                        six.raise_from(AuthenticationError(error), None)
                except ValueError:
                    pass

            raise

    def set_params_file(self, file_path):
        """
        Declare your hyper-parameter using a file in the PCS format.
        Args:
            file_path: The PCS file path
        """
        with open(file_path, "r") as pcs_file:
            pcs_content = pcs_file.read()
        self._send_params(pcs_content)

    def set_params(self, pcs_content):
        """
        Declare your hyper-parameter using a string in the PCS format.
        Args:
            pcs_content: A string in the PCS format. Leading spaces are not
                         significant.
        """
        self._send_params(pcs_content)

    def _send_params(self, pcs_content):
        """ Send the pcs content to the hyper-parameter optimization API and
        try to parse it to extract type information
        """
        # Check that we can send params only once
        if self.params_set is True:
            raise OptimizationMultipleParams()

        # Parse the pcs_content
        try:
            self.types = parse_pcs(pcs_content)
        except PCSParsingError as exc:
            # Fallback on no types and print warning
            LOGGER.warning(PARSING_ERR_MSG)
            LOGGER.warning(str(exc))
            self.types = {}
        except PCSCastingError as exc:
            # Fallback on no types and print warning
            LOGGER.warning(PARSING_ERR_MSG)
            LOGGER.warning("invalid pcs type cast: " + str(exc))
            self.types = {}
        except Exception as exc:
            LOGGER.warning("Unknown PCS error")
            LOGGER.warning("invalid pcs format: " + str(exc))
            self.types = {}

        # Send the requests
        try:
            self.connection.create(pcs_content)

            self.params_set = True
        except requests.exceptions.HTTPError as e:
            response = e.response
            # If their was a validation error, print it
            if response.status_code == 400:
                try:
                    data = response.json()
                    error = data.get("error")
                    if error:
                        six.raise_from(ValidationError(error), None)
                except ValueError:
                    pass

            raise

    def get_suggestion(self):
        """ Return a new [Suggestion](../Suggestion/#Suggestion) object
        containing values for each hyperparameter.
        """

        if self.params_set is False:
            raise NotParametrizedException()

        try:
            while True:
                response = self.connection.get_suggestion()

                data = response.json()
                suggestion = data.get("suggestion")
                if suggestion:
                    return Suggestion(suggestion, self, self.types)

                else:
                    if data.get("terminated"):
                        raise NoMoreSuggestionsAvailable()

                    time.sleep(1)
        except requests.exceptions.HTTPError as err:
            if err.response.status_code != 404:
                raise

            try:
                data = err.response.json()
                if data.get("error") == "Missing instance":
                    err_msg = "No optimization session has been found, did you called set_params or set_params_file before calling get_suggestion?"
                    six.raise_from(Exception(err_msg), None)

            except ValueError:
                raise err

    def _report_score(self, run_id, score):
        # Maximize the score
        score = -1 * score

        self.connection.report_score(run_id, score)
