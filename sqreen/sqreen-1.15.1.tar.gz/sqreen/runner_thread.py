# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Sqreen Python agent thread composition
"""
import atexit
import json
import os
import random
import sys
import threading
import time
import traceback
from copy import copy
from logging import getLogger
from threading import Event, Thread

from .__about__ import __version__
from ._vendors.urllib3.exceptions import HTTPError
from .config import CONFIG
from .constants import CHANGELOG_URL, COMPATIBILITY_URL, STATUS_URL
from .deliverer import get_deliverer
from .exceptions import UnsupportedFrameworkVersion, UnsupportedPythonVersion
from .frameworks import django_framework, flask_framework, pyramid_framework
from .http_client import Urllib3Connection
from .instrumentation import Instrumentation
from .log import configure_root_logger
from .metrics import MetricsStore
from .remote_command import RemoteCommand
from .remote_exception import RemoteException
from .runner import (
    MAX_OBS_QUEUE_LENGTH,
    MAX_QUEUE_LENGTH,
    CappedQueue,
    Runner,
    RunnerSettings,
    RunnerStop,
    process_initial_commands,
)
from .runtime_infos import (
    RuntimeInfos,
    get_parent_cmdline,
    get_process_cmdline,
)
from .session import InvalidToken, Session
from .signature import InvalidSignature
from .utils import HAS_ASYNCIO, configure_raven_breadcrumbs

if HAS_ASYNCIO:
    from .frameworks import aiohttp_framework


RUNNER_THREAD = None
RUNNER_THREAD_PID = None
RUNNER_THREAD_RESTARTING = False
RUNNER_LOCK = threading.RLock()

# Graceful timeout, max time waiting for the runner thread to exit before exiting
GRACEFUL_TIMEOUT = 4
GRACEFUL_FAIL_MSG = "Sqreen thread didn't exit after %s seconds"

LOGGER = getLogger(__name__)


def uwsgi_version_info():
    """Return uWSGI version tuple if run in uWSGI, None otherwise."""
    # Import must be delayed inside the function, because the uwsgi module is
    # not known by sqreen-start.
    try:
        import uwsgi
    except ImportError:
        return None
    else:
        return uwsgi.version_info


def should_start_runner_thread():
    """This function contains the logic used to check if the thread
    should be restarted. Beware, this function *must not* call any hooks.
    """
    global RUNNER_THREAD
    global RUNNER_THREAD_PID

    runner_stopped = False
    if RUNNER_THREAD is not None \
            and RUNNER_THREAD.runner is not None \
            and RUNNER_THREAD.runner.stop is True:
        runner_stopped = True

    return RUNNER_THREAD_PID != os.getpid() and not runner_stopped


def before_hook_point():
    global RUNNER_THREAD
    global RUNNER_THREAD_PID
    global RUNNER_THREAD_RESTARTING

    # /!\ The order of execution in this function must not change
    # without a careful review. /!\
    if should_start_runner_thread():
        # It is cheap to first call should_start_runner_thread instead
        # of just locking everytime.
        with RUNNER_LOCK:
            # If we are in a recursive call, do nothing
            if RUNNER_THREAD_RESTARTING is True:
                LOGGER.debug("The runner thread is already restarting")
                return
            # If a concurrent thread has already started the thread, do nothing
            if not should_start_runner_thread():
                LOGGER.info("The runner thread has already been started")
                return
            # Else, restart the thread
            try:
                RUNNER_THREAD_RESTARTING = True
                runner = RUNNER_THREAD.replace()
                runner.start()

                RUNNER_THREAD = runner
                RUNNER_THREAD_PID = os.getpid()

                LOGGER.info(
                    "Sucessfully started runner thread for pid: %d", os.getpid()
                )
            finally:
                RUNNER_THREAD_RESTARTING = False


def _dump_thread_stacks():
    """ Try to dump all the currently running thread stacks
    """
    try:
        msg = ["Threads stacks \n"]
        thread_name_map = {
            thread.ident: thread.name for thread in threading.enumerate()
        }

        for thread_id, stack in sys._current_frames().items():
            msg.append(
                "# Thread: id '%r', name %r"
                % (thread_id, thread_name_map[thread_id])
            )
            msg.append("".join(traceback.format_stack(stack)))

        LOGGER.debug("\n".join(msg))
    except Exception:
        LOGGER.exception("Something happened")


BLACKLISTED_PARENT_COMMANDS = (
    "ipython",
    "celery worker",
    "rq worker",
    "manage.py shell",
    "pshell",
)
BLACKLISTED_COMMANDS = BLACKLISTED_PARENT_COMMANDS + ("newrelic-admin",)

INSTRUMENTATION_TIMEOUT = 5


def get_session(url, token, app_name=None, proxy_url=None):
    """ Create a connection with the endpoint URL and a session. Returns only
    the session.
    """
    LOGGER.warning(
        "Connection to %s%s",
        url,
        " using proxy %s" % proxy_url if proxy_url else "",
    )
    con = Urllib3Connection(url, proxy_url)
    session = Session(con, token, app_name)
    return session


def post_app_sqreen_exception(data):
    """Post a Sqreen exception happening at application level.

    This function is used to report instrumentation errors. It should never
    fail.
    """
    token = CONFIG["TOKEN"]
    app_name = CONFIG["APP_NAME"]
    if not token:
        return

    session = get_session(
        CONFIG["URL"], token, app_name, proxy_url=CONFIG["PROXY_URL"]
    )
    session.post_app_sqreen_exception(data)


def start():
    """ Start the background thread and start protection
    """
    # Check if the agent is not disabled first
    try:
        disabled = int(os.getenv("SQREEN_DISABLE", 0))
    except ValueError:
        disabled = None

    # Configure logging
    configure_root_logger(CONFIG["LOG_LEVEL"], CONFIG["LOG_LOCATION"])

    # Retrieve the command used to launch the process
    command = get_process_cmdline()

    # Retrieve the parent command
    parent_command = get_parent_cmdline()

    # Check if we shouldn't launch ourselves
    for blacklisted_command in BLACKLISTED_COMMANDS:
        if blacklisted_command in command:
            LOGGER.debug(
                "Sqreen agent is disabled when running %s.",
                blacklisted_command,
            )
            return
    for blacklisted_parent_command in BLACKLISTED_PARENT_COMMANDS:
        if blacklisted_parent_command in parent_command:
            LOGGER.debug(
                "Sqreen agent is disabled when running %s.",
                blacklisted_parent_command,
            )
            return
    if hasattr(sys, "argv") and len(sys.argv) >= 2 and sys.argv[1] == "test":
        LOGGER.debug("Sqreen agent is disabled when running tests.")
        return

    if disabled:
        LOGGER.debug("Sqreen agent is disabled.")
        return

    try:
        runtime_infos = RuntimeInfos().all()
    except UnsupportedFrameworkVersion as exception:
        msg = (
            "%s version %s is not supported in this agent version.\n"
            "Sqreen agent is disabled, you're not protected.\n"
            "Documentation can be found at %s.\n"
            "Changelog can be found at %s."
        )
        LOGGER.critical(
            msg,
            exception.framework.title(),
            exception.version,
            COMPATIBILITY_URL,
            CHANGELOG_URL,
        )
        # Alter os.environ?
        return
    except UnsupportedPythonVersion as exception:
        msg = (
            "Python version %s is not supported in this agent version.\n"
            "Sqreen agent is disabled, you're not protected.\n"
            "Documentation can be found at %s.\n"
            "Changelog can be found at %s."
        )
        LOGGER.critical(
            msg, exception.python_version, COMPATIBILITY_URL, CHANGELOG_URL
        )
        return

    # Configure raven breadcrumbs at start
    configure_raven_breadcrumbs()

    global RUNNER_THREAD
    global RUNNER_THREAD_PID

    # Check for double instrumentation
    if RUNNER_THREAD is None:
        try:
            runner = RunnerThread(runtime_infos)
            runner.start()

            timeout = runner.instrumentation_done.wait(INSTRUMENTATION_TIMEOUT)

            if timeout is not True:
                msg = "Sqreen couldn't start. Check network connectivity: %s"
                LOGGER.critical(msg, STATUS_URL)
                post_app_sqreen_exception(
                    {
                        "klass": "InstrumentationTimeout",
                        "message": "Timeout during instrumentation",
                        "context": RuntimeInfos().all(),
                    }
                )

                # Also dump the stacktraces of all running threads
                _dump_thread_stacks()
            else:
                if runner.isAlive():
                    LOGGER.info("Sqreen instrumentation started successfully")
        except Exception:
            LOGGER.critical(
                "Sqreen thread fails to start, you're not protected",
                exc_info=True,
            )
            return

        RUNNER_THREAD = runner
        RUNNER_THREAD_PID = os.getpid()
    else:
        runner = RUNNER_THREAD

    return runner


def get_initial_features(config_features, login_features):
    LOGGER.debug("Login features: %s", login_features)

    final_features = copy(login_features)

    if config_features:
        parsed_config_features = {}
        try:
            parsed_config_features = json.loads(config_features)
        except (ValueError, TypeError):
            LOGGER.warning(
                "Invalid config initial features %s",
                config_features,
                exc_info=True,
            )

        if parsed_config_features and isinstance(parsed_config_features, dict):
            msg = "Override login initial features with %s"
            LOGGER.warning(msg, parsed_config_features)

            final_features.update(parsed_config_features)

            LOGGER.warning("Final features %s", final_features)

    return final_features


def get_runner(
    config,
    login_result,
    session,
    queue,
    runtime_infos,
    observations_queue,
    instrumentation,
    settings,
):
    initial_features = get_initial_features(
        config["INITIAL_FEATURES"], login_result.get("features", {})
    )

    # Get the right deliverer according to initial features
    deliverer = get_deliverer(
        initial_features.get("batch_size", 0),
        initial_features.get("max_staleness", 0),
        session,
    )
    remote_command = RemoteCommand.with_production_commands()
    metrics_store = MetricsStore()
    metrics_store.register_production_aggregators()
    metrics_store.register_default_metrics()

    # Setup the runner
    runner = Runner(
        queue,
        observations_queue,
        session,
        deliverer,
        remote_command,
        runtime_infos,
        instrumentation,
        metrics_store,
        settings,
        initial_features,
    )
    return runner


class RunnerThread(Thread):
    """ Class responsible for starting the runner and monitor it
    """

    name = "SqreenRunnerThread"

    def __init__(self, runtime_infos, queue=None, observations_queue=None,
                 instrumentation=None, settings=None):
        super(RunnerThread, self).__init__()
        self.daemon = True
        self.queue = queue or CappedQueue(MAX_QUEUE_LENGTH)
        self.observations_queue = observations_queue or CappedQueue(MAX_OBS_QUEUE_LENGTH)
        self.instrumentation_done = Event()
        self.runtime_infos = runtime_infos
        self.instrumentation = instrumentation or Instrumentation(
            self.observations_queue, self.queue, before_hook_point
        )
        self.settings = settings or RunnerSettings()
        self.runner = None
        self.started = False

    def run(self):
        """ Launch the runner
        """
        self.started = True
        LOGGER.debug("Starting Sqreen %s", __version__)
        # FIXME this part should be more tested
        while True:
            session = None
            self.runner = None

            try:
                token = CONFIG["TOKEN"]
                app_name = CONFIG["APP_NAME"]
                if not token:
                    msg = (
                        "Sorry but we couldn't find your Sqreen token.\n"
                        "Your application is NOT currently protected by Sqreen.\n"
                        "\n"
                        "Have you filled your sqreen.ini?"
                    )
                    LOGGER.critical(msg)
                    self.instrumentation_done.set()
                    return

                LOGGER.warning("Using token %s", token)

                # Initiate HTTP connection to the backend and the session
                session = get_session(
                    CONFIG["URL"], token, app_name, proxy_url=CONFIG["PROXY_URL"]
                )

                runtime_infos = dict(self.runtime_infos)
                runtime_infos["various_infos"] = {
                    k: v
                    for k, v in runtime_infos["various_infos"].items()
                    if k != "dependencies"
                }
                try:
                    login_result = session.login(runtime_infos)
                except InvalidToken:
                    msg = (
                        "Sorry but your Sqreen token appears to be invalid.\n"
                        "Your application is NOT currently protected by Sqreen.\n"
                        "\n"
                        "Please check the token against the interface"
                    )
                    LOGGER.critical(msg)
                    self.instrumentation_done.set()
                    return
                except HTTPError:
                    msg = (
                        "Sorry but Sqreen's backend appears to be unavailable.\n"
                        "Your application is NOT currently protected by Sqreen.\n"
                        "\n"
                        "Please check http://sqreen.status.io for outage.\n"
                        "\n"
                        "Otherwise, back.sqreen.io may be blocked by your server's network.\n"
                        "If necessary, you tell Sqreen to connect over a proxy.\n"
                        "Please visit https://docs.sqreen.com/python/configuration/ for more details."
                    )
                    LOGGER.critical(msg)
                    self.instrumentation_done.set()
                    return

                LOGGER.info("Login success")

                self.runner = get_runner(
                    CONFIG,
                    login_result,
                    session,
                    self.queue,
                    self.runtime_infos,
                    self.observations_queue,
                    self.instrumentation,
                    self.settings,
                )

                # Process the initial commands
                process_initial_commands(login_result, self.runner)

                retry = 3
                while True:
                    try:
                        # if we did not receive instrumentation_enable, try
                        # to get it faster before the MainThread stops waiting.
                        while not self.instrumentation.enabled and retry > 0:
                            retry -= 1
                            self._random_sleep(2.0)
                            self.runner.do_heartbeat()
                        self.instrumentation_done.set()
                        self.runner.run()
                    except HTTPError:
                        LOGGER.exception(
                            "An HTTP error occured, restarting runner"
                        )
                        try:
                            session.post_sqreen_exception(
                                RemoteException(sys.exc_info()).to_dict()
                            )
                        except HTTPError:
                            pass
                        self._random_sleep()
                    else:
                        # If the runner exits normally, return.
                        return
            except Exception as exc:
                LOGGER.exception("An unexpected exception occured")

                if session is not None and session.is_connected():
                    if isinstance(exc, InvalidSignature):
                        remote_exception = RemoteException(
                            exc.exc_info, exc.callback_payload
                        )
                    else:
                        remote_exception = RemoteException(sys.exc_info())
                    try:
                        session.post_sqreen_exception(
                            remote_exception.to_dict()
                        )
                        session.logout()
                    except HTTPError:
                        LOGGER.exception("An HTTP error occured while logout")
                    except Exception:
                        LOGGER.exception("Exception while logout")
                        return

                try:
                    self.instrumentation.deinstrument_all()
                except Exception:
                    # We did not managed to remove instrumentation, state is unclear:
                    # terminate thread
                    LOGGER.exception("Exception while trying to clean-up")
                    return

                self._random_sleep()

    def quick_exit(self):
        """Check for early exit."""
        if os.environ.get("SQREEN_SKIP_LOGOUT", False):
            return True
        # uWSGI 2.0.15 may segfault upon exiting.
        # See https://github.com/unbit/uwsgi/issues/1651.
        uwsgi_vers = uwsgi_version_info()
        if uwsgi_vers and uwsgi_vers >= (2, 0, 15):
            return True
        elif "django" in sys.modules:
            return django_framework.DjangoRequest.DEBUG_MODE
        elif "flask" in sys.modules:
            return flask_framework.FlaskRequest.DEBUG_MODE
        elif "pyramid" in sys.modules:
            return pyramid_framework.PyramidRequest.DEBUG_MODE
        elif HAS_ASYNCIO and "aiohttp" in sys.modules:
            return aiohttp_framework.AioHTTPRequest.DEBUG_MODE
        return False

    def start(self):
        """Start the runner thread."""
        atexit.register(self.graceful_stop)
        return super(RunnerThread, self).start()

    def graceful_stop(self, force_quick_exit=False):
        """Gracefully stop the runner thread and wait for its termination."""
        self.queue.put(RunnerStop)

        if force_quick_exit or self.quick_exit():
            LOGGER.warning("Quick exit, don't logout")
            return

        try:
            self.join(GRACEFUL_TIMEOUT)
        except RuntimeError:
            logger = getLogger(__name__)
            logger.warning(GRACEFUL_FAIL_MSG, GRACEFUL_TIMEOUT)
        else:
            if self.isAlive():
                logger = getLogger(__name__)
                logger.warning(GRACEFUL_FAIL_MSG, GRACEFUL_TIMEOUT)

    def replace(self, **kwargs):
        """Create a new runner thread instance."""
        nkwargs = dict(
            queue=self.queue,
            observations_queue=self.observations_queue,
            instrumentation=self.instrumentation,
            settings=self.settings,
        )
        nkwargs.update(kwargs)
        return self.__class__(RuntimeInfos().all(), **nkwargs)

    @classmethod
    def _random_sleep(cls, max_delay=10.0):
        """Sleep for a random duration before trying again."""
        delay = random.uniform(0, max_delay)
        LOGGER.info("Sleeping %s seconds before retry", delay)
        time.sleep(delay)
