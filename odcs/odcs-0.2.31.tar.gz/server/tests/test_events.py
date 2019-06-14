# Copyright (c) 2017  Red Hat, Inc.
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
# Written by Chenxiong Qi <cqi@redhat.com>

import json
import six
import unittest

from mock import patch

from odcs.server import conf
from odcs.server import db
from odcs.server.models import Compose
from odcs.server.pungi import PungiSourceType
from odcs.common.types import COMPOSE_RESULTS
from odcs.common.types import COMPOSE_STATES
from .utils import ModelsBaseTest

try:
    import rhmsg
except ImportError:
    rhmsg = None

try:
    import fedmsg
except ImportError:
    fedmsg = None


@unittest.skipUnless(rhmsg, 'rhmsg is required to run this test case.')
@unittest.skipIf(six.PY3, 'rhmsg has no Python 3 package so far.')
class TestRHMsgSendMessageWhenComposeIsCreated(ModelsBaseTest):
    """Test send message when compose is created"""

    disable_event_handlers = False

    def setUp(self):
        super(TestRHMsgSendMessageWhenComposeIsCreated, self).setUp()

        # Real lock is not required for running tests
        self.mock_lock = patch('threading.Lock')
        self.mock_lock.start()

    def tearDown(self):
        self.mock_lock.stop()

    def setup_composes(self):
        self.compose = Compose.create(db.session,
                                      "mine",
                                      PungiSourceType.KOJI_TAG,
                                      "f25",
                                      COMPOSE_RESULTS["repository"],
                                      3600)
        db.session.commit()

    @patch.object(conf, 'messaging_backend', new='rhmsg')
    @patch('rhmsg.activemq.producer.AMQProducer')
    @patch('proton.Message')
    def assert_messaging(self, compose, Message, AMQProducer):
        db.session.commit()

        self.assertEqual(
            json.dumps({'event': 'state-changed', 'compose': compose.json()}),
            Message.return_value.body)

        producer_send = AMQProducer.return_value.__enter__.return_value.send
        producer_send.assert_called_once_with(Message.return_value)

    def test_send_message(self):
        compose = Compose.create(db.session,
                                 "me",
                                 PungiSourceType.MODULE,
                                 "testmodule-master",
                                 COMPOSE_RESULTS["repository"],
                                 3600)

        self.assert_messaging(compose)

    def test_message_on_state_change(self):
        compose = db.session.query(Compose).filter(
            Compose.id == self.compose.id).all()[0]
        compose.state = COMPOSE_STATES['generating']

        self.assert_messaging(compose)


@unittest.skipUnless(fedmsg, 'fedmsg is required to run this test case.')
class TestFedMsgSendMessageWhenComposeIsCreated(ModelsBaseTest):
    """Test send message when compose is created"""

    disable_event_handlers = False

    def setUp(self):
        super(TestFedMsgSendMessageWhenComposeIsCreated, self).setUp()

        # Real lock is not required for running tests
        self.mock_lock = patch('threading.Lock')
        self.mock_lock.start()

    def tearDown(self):
        self.mock_lock.stop()

    def setup_composes(self):
        self.compose = Compose.create(db.session,
                                      "mine",
                                      PungiSourceType.KOJI_TAG,
                                      "f25",
                                      COMPOSE_RESULTS["repository"],
                                      3600)
        db.session.commit()

    @patch.object(conf, 'messaging_backend', new='fedmsg')
    @patch('fedmsg.publish')
    def assert_messaging(self, compose, publish):
        db.session.commit()
        publish.assert_called_once_with(
            topic='compose.state-changed',
            msg={'event': 'state-changed', 'compose': compose.json()}
        )

    def test_send_message(self):
        compose = Compose.create(db.session,
                                 "me",
                                 PungiSourceType.MODULE,
                                 "testmodule-master",
                                 COMPOSE_RESULTS["repository"],
                                 3600)

        self.assert_messaging(compose)

    def test_message_on_state_change(self):
        compose = db.session.query(Compose).filter(
            Compose.id == self.compose.id).all()[0]
        compose.state = COMPOSE_STATES['generating']

        self.assert_messaging(compose)
