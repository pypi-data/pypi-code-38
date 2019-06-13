# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Email Bouncer Daemon
"""

from __future__ import unicode_literals

import os
import re
import time
import imaplib
import datetime
import logging
from email import message_from_string

from rattail.db import Session, model
from rattail.daemon import Daemon
from rattail.bouncer.config import load_profiles
from rattail.threads import Thread


log = logging.getLogger(__name__)


class BouncerDaemon(Daemon):
    """
    Daemon responsible for checking IMAP folders and detecting email bounces,
    and adding them to the workflow queue in the database.
    """

    def run(self):
        """
        Starts watcher and worker threads according to configuration.
        """
        watched = load_profiles(self.config)
        for key, profile in watched.items():

            # Create a thread for watching the IMAP folder.
            watcher = IMAPWatcher(profile)
            name = 'watcher_{0}'.format(key)
            thread = Thread(target=watcher, name=name)
            thread.daemon = True
            thread.start()
            log.info("started IMAP watcher thread: {0}".format(name))

        # Loop indefinitely.  Since this is the main thread, the app will
        # terminate when this method ends; all other threads are "subservient"
        # to this one.
        while True:
            time.sleep(.01)


class IMAPWatcher(object):
    """
    Abstraction to make watching an IMAP folder a little more organized.
    Instances of this class are used as callable targets when the daemon starts
    watcher threads.  They are responsible for polling the IMAP folder and
    processing any messages found there.
    """
    uid_pattern = re.compile(r'^\d+ \(UID (?P<uid>\d+)')

    def __init__(self, profile):
        self.profile = profile
        self.handler = profile.handler
        self.server = None

    def get_uid(self, response):
        match = self.uid_pattern.match(response)
        if match:
            return match.group('uid')

    def __call__(self):
        recycled = None
        while True:

            if self.server is None:
                self.server = imaplib.IMAP4_SSL(self.profile.imap_server)
                result = self.server.login(self.profile.imap_username, self.profile.imap_password)
                log.debug("IMAP server login result: {0}".format(repr(result)))
                recycled = datetime.datetime.utcnow()

            self.server.select(self.profile.imap_folder_inbox)

            try:
                self.process_all_messages()
            except Exception as error:
                log.exception("processing failed for server {0}".format(self.profile.imap_server))

            time.sleep(self.profile.imap_delay)

            # If recycle time limit has been reached, close and reopen the IMAP connection.
            if (datetime.datetime.utcnow() - recycled).seconds >= self.profile.imap_recycle:
                log.debug("recycle time limit reached, disposing of current connection")
                self.server.close()
                self.server.logout()
                self.server = None

        self.server.close()
        self.server.logout()

    def process_all_messages(self):
        log.debug("invoking IMAP4.search()")
        code, items = self.server.uid('search', None, 'ALL')
        if code == 'OK':
            msg_ids = items[0].split()
            if msg_ids:
                self.process_messages(msg_ids)
        else:
            log.error("IMAP4.search() returned bad code: {0}".format(repr(code)))

    def process_messages(self, msg_uids):
        session = Session()
        for msg_uid in msg_uids:
            code, msg_data = self.server.uid('fetch', msg_uid, '(RFC822)')
            if code == 'OK':
                assert len(msg_data) == 2
                assert msg_data[1] == ')'
                response, msg_body = msg_data[0]
                self.process_message(session, msg_body)
                self.move_message(msg_uid)
            else:
                log.error("IMAP4.fetch() returned bad code: {0}, {1}".format(
                    repr(code), repr(msg_data)))
        session.commit()
        session.close()

    def process_message(self, session, msg_body):
        msg = message_from_string(msg_body)
        warnings, failures = self.handler.get_all_failures(msg)
        if failures:
            self.make_bounce(session, msg, failures, msg_body)
        elif warnings:
            log.warning("found message delivery warning for: {0}".format(warnings))
        else:
            log.debug("found message with nothing interesting")

    def make_bounce(self, session, msg, failures, msg_body):
        log.info("adding bounce for: {0}".format(failures))
        bounce = self.handler.make_bounce(msg, failures)
        session.add(bounce)
        session.flush()
        self.handler.store_message_file(bounce, msg_body)
        log.info("invoking handler to process bounce: {0}".format(self.handler))
        self.handler.process_bounce(bounce)

    def move_message(self, msg_uid):
        code, response = self.server.uid('COPY', msg_uid, self.profile.imap_folder_backup)
        if code == 'OK':
            code, response = self.server.uid('STORE', msg_uid, '+FLAGS', '(\Deleted)')
            if code == 'OK':
                code, response = self.server.expunge()
                if code != 'OK':
                    log.error("IMAP.expunge() returned bad code: {0}".format(repr(code)))
            else:
                log.error("IMAP.store(uid={0}) returned bad code: {1}".format(
                    repr(msg_uid), repr(code)))
        else:
            log.error("IMAP.copy(uid={0}) returned bad code: {1}".format(
                repr(msg_uid), repr(code)))
