# -*- coding: utf-8 -*-
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

import os
import unittest

from odcs.server import db
from sqlalchemy import event
from odcs.server.events import cache_composes_if_state_changed
from odcs.server.events import start_to_publish_messages
from odcs.server import conf

from flask_sqlalchemy import SignallingSession
from mock import patch


class AnyStringWith(str):
    def __eq__(self, other):
        return self in str(other)


class ConfigPatcher(object):

    def __init__(self, config_obj):
        self.objects = []
        self.config_obj = config_obj

    def patch(self, key, value):
        try:
            obj = patch.object(self.config_obj, key, new=value)
        except Exception:
            self.stop()
            raise
        self.objects.append(obj)

    def start(self):
        for obj in self.objects:
            obj.start()

    def stop(self):
        for obj in self.objects:
            obj.stop()


class ModelsBaseTest(unittest.TestCase):
    """Base test case for models

    Database and schemas are initialized on behalf of developers.
    """

    disable_event_handlers = True

    def setUp(self):
        # Not all tests need handlers of event after_flush and after_commit.
        if event.contains(SignallingSession, 'after_flush',
                          cache_composes_if_state_changed):
            event.remove(SignallingSession, 'after_flush',
                         cache_composes_if_state_changed)
        if event.contains(SignallingSession, 'after_commit',
                          start_to_publish_messages):
            event.remove(SignallingSession, 'after_commit',
                         start_to_publish_messages)

        db.session.remove()
        db.drop_all()
        db.create_all()
        db.session.commit()

        setup_composes = getattr(self, 'setup_composes', None)
        if setup_composes is not None:
            assert callable(setup_composes)
            setup_composes()

        if hasattr(self, 'setup_composes'):
            getattr(self, 'setup_composes')()

        # And, if tests which need such event handlers or just tests those
        # handlers, add them back.
        if not self.disable_event_handlers:
            event.listen(SignallingSession, 'after_flush',
                         cache_composes_if_state_changed)
            event.listen(SignallingSession, 'after_commit',
                         start_to_publish_messages)

        # Make Compose.toplevel_work_dir to work everytime.
        self.patch_glob = patch("odcs.server.models.glob.glob")
        self.glob = self.patch_glob.start()
        self.glob.return_value = [
            os.path.join(conf.target_dir, "odcs-1-2018-1")]

    def tearDown(self):
        if not self.disable_event_handlers:
            event.remove(SignallingSession, 'after_flush',
                         cache_composes_if_state_changed)
            event.remove(SignallingSession, 'after_commit',
                         start_to_publish_messages)

        db.session.remove()
        db.drop_all()
        db.session.commit()

        # Nothing special here. Just do what should be done in tearDown to
        # to restore enviornment for each test method.
        event.listen(SignallingSession, 'after_flush',
                     cache_composes_if_state_changed)
        event.listen(SignallingSession, 'after_commit',
                     start_to_publish_messages)

        self.patch_glob.stop()
