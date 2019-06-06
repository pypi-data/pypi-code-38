# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
import logging
from collections import defaultdict

from .events import RequestRecord
from .runner import MetricsEvent

LOGGER = logging.getLogger(__name__)


class RequestRecorder:
    """Store observations related to a request."""

    def __init__(self):
        self.clear()

    def clear(self):
        """Clear all observations."""
        self.report = False
        self.payload_sections = set()
        self.observations = defaultdict(list)
        self.identity = None

    def observe(self, what, observation, payload_sections=None, report=True):
        """Record an observation."""
        if what == "sdk":
            name = observation[0]
            if name == "identify":
                self.identity = observation[2]
            elif self.identity and name == "track":
                identity = observation[3].get("user_identifiers")
                if identity and identity != self.identity:
                    LOGGER.warning(
                        "sqreen.identify and sqreen.track have been called "
                        "with different user_identifiers values"
                    )
        self.observations[what].append(observation)
        if payload_sections:
            self.payload_sections.update(payload_sections)
        if report:
            self.report = True

    def flush(self, request, response, payload_creator, queue, observation_queue):
        """Flush all observations."""
        if self.identity:
            # Tag unidentified track events with identity.
            for observation in self.observations["sdk"]:
                if observation[0] != "track":
                    continue
                track_options = observation[3]
                track_options.setdefault("user_identifiers", self.identity)

        if self.report:
            payload = payload_creator.get_payload(
                request, response, self.payload_sections
            )
            payload["observed"] = self.observations
            queue.put(RequestRecord(payload))
        else:
            self._put_metrics(queue, observation_queue)
        self.clear()

    def _put_metrics(self, queue, observation_queue):
        for observation in self.observations["observations"]:
            observation_queue.put(observation)
        if observation_queue.half_full():
            queue.put(MetricsEvent)
