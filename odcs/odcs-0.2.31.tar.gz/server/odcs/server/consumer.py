# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import fedmsg.consumers

from odcs.server import log, conf, db
from odcs.server.backend import ComposerThread, RemoveExpiredComposesThread
from odcs.server.models import Compose
from odcs.server.utils import retry


class ODCSConsumer(fedmsg.consumers.FedmsgConsumer):
    """
    This is triggered by running fedmsg-hub. This class is responsible for
    ingesting and processing messages from the message bus.
    """
    config_key = 'odcsconsumer'

    def __init__(self, hub):
        # set topic before super, otherwise topic will not be subscribed
        messaging_topic = conf.messaging_topic_prefix + conf.messaging_topic
        internal_messaging_topic = conf.messaging_topic_prefix + \
            conf.internal_messaging_topic
        self.topic = [messaging_topic, internal_messaging_topic]
        log.debug('Setting topics: {}'.format(', '.join(self.topic)))
        super(ODCSConsumer, self).__init__(hub)

        self.composer = ComposerThread()
        self.remove_expired_compose_thread = RemoveExpiredComposesThread()

        # These two values are typically provided either by the unit tests or
        # by the local build command.  They are empty in the production environ
        self.stop_condition = hub.config.get('odcs.stop_condition')
        initial_messages = hub.config.get('odcs.initial_messages', [])
        for msg in initial_messages:
            self.incoming.put(msg)

    def shutdown(self):
        log.info("Scheduling shutdown.")
        from moksha.hub.reactor import reactor
        reactor.callFromThread(self.hub.stop)
        reactor.callFromThread(reactor.stop)

    def validate(self, message):
        if conf.messaging_backend == 'fedmsg':
            super(ODCSConsumer, self).validate(message)

    def consume(self, message):
        topic, inner_msg = self.parse_message(message)

        # Primary work is done here.
        try:
            self.process_message(topic, inner_msg)
        except Exception:
            log.exception('Failed while handling {0!r}'.format(message))

        # Commit the session to ensure that database transaction is closed and
        # does not remain in Idle state acquiring the table lock.
        db.session.commit()

        if self.stop_condition and self.stop_condition(message):
            self.shutdown()

    def parse_message(self, message):
        """
        Returns the topic of message and inner message which we actually care
        about.
        """
        if 'topic' not in message:
            raise ValueError(
                'The messaging format "{}" is not supported'.format(conf.messaging_backend))

        inner_msg = message.get('body')
        inner_msg = inner_msg.get('msg', inner_msg)
        return message["topic"], inner_msg

    @retry(wait_on=RuntimeError)
    def get_odcs_compose(self, compose_id):
        """
        Gets the compose from ODCS DB.
        """
        compose = Compose.query.filter(Compose.id == compose_id).first()
        if not compose:
            raise RuntimeError("No compose with id %d in ODCS DB." % compose_id)
        return compose

    def process_message(self, topic, msg):
        """
        Handles the parsed message `msg` of topic `topic`.
        """
        log.debug("Received: %r", msg)
        if topic.endswith(conf.messaging_topic):
            compose_state = msg["compose"]["state_name"]
            if compose_state != "wait":
                return
            compose_id = msg["compose"]["id"]
            compose = self.get_odcs_compose(compose_id)
            self.composer.generate_new_compose(compose)
        elif topic.endswith(conf.internal_messaging_topic):
            self.remove_expired_compose_thread.do_work()
            self.composer.pickup_waiting_composes()
            self.composer.fail_lost_generating_composes()
