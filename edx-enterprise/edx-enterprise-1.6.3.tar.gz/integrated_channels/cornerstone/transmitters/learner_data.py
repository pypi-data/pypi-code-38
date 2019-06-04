# -*- coding: utf-8 -*-
"""
Class for transmitting learner data to Cornerstone.
"""

from __future__ import absolute_import, unicode_literals

from integrated_channels.cornerstone.client import CornerstoneAPIClient
from integrated_channels.integrated_channel.transmitters.learner_data import LearnerTransmitter


class CornerstoneLearnerTransmitter(LearnerTransmitter):
    """
    This endpoint is intended to receive learner data routed from the integrated_channel app that is ready to be
    sent to Cornerstone.
    """

    def __init__(self, enterprise_configuration, client=CornerstoneAPIClient):
        """
        By default, use the ``CornerstoneAPIClient`` for learner data transmission to Cornerstone.
        """
        super(CornerstoneLearnerTransmitter, self).__init__(
            enterprise_configuration=enterprise_configuration,
            client=client
        )

    def transmit(self, payload, **kwargs):
        """
        Send a completion status call to Cornerstone using the client.

        Args:
            payload: The learner completion data payload to send to Cornerstone
        """
        kwargs['app_label'] = 'cornerstone'
        kwargs['model_name'] = 'CornerstoneLearnerDataTransmissionAudit'
        kwargs['remote_user_id'] = 'cornerstone_user_email'
        super(CornerstoneLearnerTransmitter, self).transmit(payload, **kwargs)
