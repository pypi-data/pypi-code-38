# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Main runner module
"""

import logging
from datetime import datetime
from time import time

from sqreen.performance_metrics import PerformanceMetricsSettings

from .actions import ACTION_STORE
from .deliverer import get_deliverer
from .ip_radix import Radix
from .list_filters import RequestPrefixListFilter

try:
    # Python2
    from queue import Empty, Queue, Full
except ImportError:
    from Queue import Empty, Queue, Full

MAX_QUEUE_LENGTH = 100
MAX_OBS_QUEUE_LENGTH = 1000

LOGGER = logging.getLogger(__name__)


class RunnerStop(object):
    """ Placeholder event for asking the runner to stop
    """


class MetricsEvent(object):
    """ Placeholder for asking observations aggregation to run
    """


class CappedQueue(object):
    """ Capped queue with opiniatied methods
    """

    def __init__(self, maxsize=None):
        if maxsize is None:
            maxsize = MAX_QUEUE_LENGTH

        self.maxsize = maxsize
        self.queue = Queue(self.maxsize)

    def get(self, timeout, block=True):
        """ Wait for up to timeout for an item to return and block while
        waiting
        """
        return self.queue.get(timeout=timeout, block=block)

    def get_nowait(self):
        """ Get without waiting, raise queue.Empty if nothing is present
        """
        return self.queue.get_nowait()

    def put(self, item):
        """ Tries to put an item to the queue, if the queue is empty, pop an
        item and try again
        """
        pushed = False
        while pushed is False:
            try:
                self.queue.put_nowait(item)
                pushed = True
            except Full:
                try:
                    self.queue.get_nowait()
                    self.queue.task_done()
                except Empty:
                    pass

    def clear(self):
        """ Clear all items in the queue
        """
        with self.queue.mutex:
            self.queue.queue.clear()

    def half_full(self):
        """ Return True if the current queue size if at least half the maxsize
        """
        return self.queue.qsize() > (self.maxsize / 2.)


class RunnerSettings(object):
    """ Various values that need to be shared across threads
    """

    def __init__(self):
        self.ips_whitelist = Radix(None)
        self.paths_whitelist = RequestPrefixListFilter()

    def set_ips_whitelist(self, addresses):
        """ Replace the current list of whitelisted IP networks
        """
        self.ips_whitelist.clear()
        for address in addresses:
            self.ips_whitelist.insert(address, '/' in address)

    def ips_whitelist_match(self, address):
        """ Return the first matching IP network, or None if no match could be
        found.
        """
        if address:
            return self.ips_whitelist.match(address)

    def set_paths_whitelist(self, paths):
        """ Replace the current list of whitelisted request path prefixes
        """
        self.paths_whitelist.reset(paths)

    def paths_whitelist_match(self, path):
        """ Return the first matching request path prefix, or None if no match
        could be found.
        """
        return self.paths_whitelist.match(path)

    def whitelist_match(self, request):
        """ Return the first matching IP network or request path prefix, or
        None if no match could be found.
        """
        ip = self.ips_whitelist_match(request.client_ip)
        if ip is not None:
            return ip
        prefix = self.paths_whitelist_match(request.path)
        if prefix is not None:
            return prefix


def process_initial_commands(initial_payload, runner):
    """ Process the initial non-standard login payload
    """
    commands = initial_payload.get("commands", [])

    # Preprocess commands first
    for command in commands:
        if command["name"] == "instrumentation_enable":
            rulespack_id = initial_payload.get("pack_id")
            rules = initial_payload.get("rules")

            if not rulespack_id or not rules:
                msg = "Invalid login payload, pack_id %s, rules %s"
                LOGGER.warning(msg, rulespack_id, rules)
            else:
                command["params"] = (rulespack_id, rules)

    # Process commands normally
    if commands:
        runner.process_commands(commands)

    actions = initial_payload.get("actions")
    ACTION_STORE.reload_from_dicts(actions or [])


class Runner(object):
    """ Main runner class

    Its job is to be the orchestrator and receiver for application communication
    It interacts with the backend through session, call heartbeat himself,
    execute commands and forward events
    """

    # Heartbeat delay is 5 minutes by default
    HEARTBEAT_DELAY = 300

    def __init__(
        self,
        queue,
        observation_queue,
        session,
        deliverer,
        remote_command,
        runtime_infos,
        instrumentation,
        metrics_store,
        settings,
        initial_features=None,
    ):
        self.logger = logging.getLogger(
            "{}.{}".format(self.__module__, self.__class__.__name__)
        )
        self.queue = queue
        self.observation_queue = observation_queue
        self.deliverer = deliverer
        self.remote_command = remote_command
        self.runtime_infos = runtime_infos
        self.instrumentation = instrumentation
        self.metrics_store = metrics_store
        self.settings = settings
        self.stop = False

        # Save the time runner started for checking warmup period termination
        self.started = time()

        if initial_features is None:
            initial_features = {}

        # The first time we shouldn't wait too long before sending heartbeat
        self.heartbeat_delay = initial_features.get(
            "heartbeat_delay", self.HEARTBEAT_DELAY
        )

        self.performance_metrics_settings =\
            PerformanceMetricsSettings.from_features(initial_features)

        self.budget_in_ms = None  # currently only used for AgentDaemon

        self.whitelisted_metric = initial_features.get(
            "whitelisted_metric", True
        )

        self.last_heartbeat_request = 0
        self.last_post_metrics_request = time()

        self.session = session

        # Features
        self.logger.debug("Initial features %s", self.features_get())

        # Next things to send on next heartbeat
        self.next_commands_results = {}

    def run(self):
        """ Infinite loop
        """
        self.logger.debug("Starting runner")
        while self.stop is False:
            self.run_once()
        self.logger.debug("Exiting now")

    def run_once(self, block=True):
        """ Tries to pop a message or send an heartbeat
        """
        try:
            event = self.queue.get(timeout=self.sleep_delay, block=block)
            self.logger.debug(
                "Run once, event: %s after %ss sleep delay",
                event,
                self.sleep_delay,
            )
            self.handle_message(event)

            # Exit now if should stop
            if self.stop:
                return
        except Empty:
            self.logger.debug(
                "No message after %ss sleep delay", self.sleep_delay
            )

        # Aggregate observations in transit in observations queue
        self.aggregate_observations()

        if self._should_do_heartbeat():
            self.do_heartbeat()

        # Tick the deliverer to publish batch if necessary
        self.deliverer.tick()

    @property
    def sleep_delay(self):
        """ Compute the sleeping delay by taking the heartbeat
        """
        return self.heartbeat_delay

    def handle_message(self, event):
        """ Handle incoming message
        Process RunnerStop message or pass event to the deliverer
        """
        if event is RunnerStop:
            self.logger.debug("RunnerStop found, logout")
            self.logout()
            self.stop = True
        elif event is MetricsEvent:
            self.aggregate_observations()
        else:
            self.deliverer.post_event(event)

    def process_commands(self, commands):
        """ handle commands
        """
        result = self.remote_command.process_list(commands, self)
        self.next_commands_results.update(result)

    def do_heartbeat(self):
        """ Do an heartbeat, publish finished metrics from MetricsStore and
        past commands results
        """
        metrics = self.metrics_store.get_data_to_publish(
            datetime.utcnow(), force_finalize=False
        )
        payload = {
            "command_results": self.next_commands_results,
            "metrics": metrics,
        }
        res = self.session.heartbeat(payload)
        self.last_heartbeat_request = time()

        # Clean sent command results
        self.next_commands_results = {}

        if res is not None:
            self.process_commands(res["commands"])

    def aggregate_observations(self):
        """ Empty the observation queue and update the metric store
        with the observations in the queue.
        """
        try:
            while True:
                observation = self.observation_queue.get_nowait()
                self.metrics_store.update(*observation)
        except Empty:
            pass

    def publish_metrics(self):
        """ Publish finished metrics from MetricsStore
        """
        self.session.post_metrics(
            self.metrics_store.get_data_to_publish(datetime.utcnow())
        )

    def _should_do_heartbeat(self):
        """ Check if we should send an heartbeat because the delay is overdue
        """
        return (self.last_heartbeat_request + self.heartbeat_delay) < time()

    def logout(self):
        """ Run cleanup
        """
        self.logger.debug("Logout")

        # Flush metrics
        self.aggregate_observations()
        self.publish_metrics()

        # Drain deliverer
        self.deliverer.drain(resiliently=False)

        self.session.logout()

        # Mark itself as stopped if it's not the end of the application
        self.stop = True

    ###
    # Features
    ###

    def features_get(self):
        """ Returns the current values for all features switches
        """
        res = {
            "heartbeat_delay": self.heartbeat_delay,
            "batch_size": self.deliverer.batch_size,
            "max_staleness": self.deliverer.original_max_staleness,
            "call_counts_metrics_period": self.metrics_store.get_metric_period(
                "sqreen_call_counts"
            ),
            "whitelisted_metric": self.whitelisted_metric,
        }
        res.update(self.performance_metrics_settings.as_features())
        return res

    def set_heartbeat_delay(self, heartbeat_delay):
        """ Update the heartbeat delay
        """
        self.heartbeat_delay = heartbeat_delay

    def set_performance_metrics_settings(self, new_perf_met_set):
        self.performance_metrics_settings = new_perf_met_set

    def performance_metrics_period(self):
        return self.performance_metrics_settings.period

    def set_call_counts_metrics_period(self, call_counts_metrics_period):
        self.metrics_store.register_metric(
            "sqreen_call_counts", "Sum", call_counts_metrics_period
        )

    def set_whitelisted_metric(self, enabled):
        self.whitelisted_metric = enabled

    def set_deliverer(self, batch_size, max_staleness):
        # Drain current deliverer
        self.deliverer.drain(resiliently=True)

        # Replace current deliverer
        self.deliverer = get_deliverer(batch_size, max_staleness, self.session)

    def set_ips_whitelist(self, addresses):
        """ Update current RunnerSettings ips_whitelist
        """
        self.logger.debug("Set IPs whitelist on settings %r", self.settings)
        self.settings.set_ips_whitelist(addresses)

    def set_paths_whitelist(self, paths):
        """ Update current RunnerSettings paths_whitelist
        """
        self.logger.debug("Set paths whitelist on settings %r", self.settings)
        self.settings.set_paths_whitelist(paths)
