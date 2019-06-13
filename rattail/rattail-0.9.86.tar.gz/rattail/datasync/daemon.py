# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
DataSync for Linux
"""

from __future__ import unicode_literals, absolute_import

import sys
import time
import datetime
import logging
from traceback import format_exception

from rattail.db import api
from rattail.daemon import Daemon
from rattail.threads import Thread
from rattail.datasync.config import load_profiles
from rattail.datasync.util import get_lastrun, get_lastrun_setting, get_lastrun_timefmt
from rattail.mail import send_email
from rattail.time import make_utc, localtime


log = logging.getLogger(__name__)


class DataSyncDaemon(Daemon):
    """
    Linux daemon implementation of DataSync.
    """

    def run(self):
        """
        Starts watcher and consumer threads according to configuration.
        """
        for key, profile in load_profiles(self.config).items():

            # Create watcher thread for the profile.
            name = '{}-watcher'.format(key)
            log.debug("starting thread '{}' with watcher: {}".format(name, profile.watcher_spec))
            thread = Thread(target=watch_for_changes, name=name, args=(self.config, profile.watcher))
            thread.daemon = True
            thread.start()

            # Create consumer threads, unless watcher consumes itself.
            if not profile.watcher.consumes_self:

                # Create a thread for each "isolated" consumer.
                # for consumer in profile.isolated_consumers:
                for consumer in profile.consumers:
                    name = '{}-consumer-{}'.format(key, consumer.key)
                    log.debug("starting thread '%s' with consumer: %s", name, consumer.spec)
                    thread = Thread(target=consume_changes_perpetual, name=name, args=(self.config, profile, consumer))
                    thread.daemon = True
                    thread.start()

        # Loop indefinitely.  Since this is the main thread, the app will
        # terminate when this method ends; all other threads are "subservient"
        # to this one.
        while True:
            time.sleep(.01)


def watch_for_changes(config, watcher):
    """
    Target for DataSync watcher threads.
    """
    # Let watcher do any setup it needs.
    watcher.setup()

    # the 'last run' value is maintained as zone-aware UTC
    lastrun = get_lastrun(config, watcher.key)
    lastrun_setting = get_lastrun_setting(config, watcher.key)
    timefmt = get_lastrun_timefmt(config)

    while True:

        thisrun = make_utc(tzinfo=True)
        attempts = 0
        errtype = None
        while True:

            attempts += 1

            try:
                changes = watcher.get_changes(lastrun)

            except Exception as error:

                exc_type, exc, traceback = sys.exc_info()

                # If we've reached our final attempt, stop retrying.
                if attempts >= watcher.retry_attempts:
                    log.warning("attempt #{} failed calling `watcher.get_changes()`, this thread "
                                "will now *terminate* until datasync restart".format(attempts),
                                exc_info=True)
                    send_email(config, 'datasync_error_watcher_get_changes', {
                        'watcher': watcher,
                        'error': exc,
                        'attempts': attempts,
                        'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
                        'datasync_url': config.datasync_url(),
                    })
                    raise

                # If this exception is not the first, and is of a different type
                # than seen previously, do *not* continue to retry.
                if errtype is not None and not isinstance(error, errtype):
                    log.exception("new exception differs from previous one(s), "
                                  "giving up on watcher.get_changes()")
                    raise

                # Record the type of exception seen, and pause for next retry.
                errtype = type(error)
                log.warning("attempt #{} failed for '{}' watcher.get_changes()".format(attempts, watcher.key))
                log.debug("pausing for {} seconds before making attempt #{} of {}".format(
                    watcher.retry_delay, attempts + 1, watcher.retry_attempts))
                if watcher.retry_delay:
                    time.sleep(watcher.retry_delay)

            else:
                # watcher got changes okay, so record/process and prune, then
                # break out of inner loop to reset the attempt count for next grab
                lastrun = thisrun
                api.save_setting(None, lastrun_setting, lastrun.strftime(timefmt))
                if changes:
                    log.debug("got {} changes from '{}' watcher".format(len(changes), watcher.key))
                    # TODO: and what if this step fails..??
                    if record_or_process_changes(watcher, changes):
                        prune_changes(watcher, changes)
                break

        # sleep a moment between successful change grabs
        time.sleep(watcher.delay)


def record_or_process_changes(watcher, changes):
    """
    Now that we have changes from the watcher, we'll either record them as
    proper DataSync changes, or else let the watcher process them (if it
    consumes self).
    """
    from rattail.db import Session, model

    # If watcher consumes itself, then it will process its own changes.  Note
    # that there are no assumptions made about the format or structure of these
    # change objects.
    if watcher.consumes_self:
        session = Session()
        try:
            watcher.process_changes(session, changes)
        except Exception:
            log.exception("error calling watcher.process_changes()")
            session.rollback()
            raise
        else:
            session.commit()
            log.debug("watcher has consumed its own changes")
            return True
        finally:
            session.close()

    else:
        # Give all change stubs the same timestamp, to help identify them
        # as a "batch" of sorts, so consumers can process them as such.
        now = datetime.datetime.utcnow()

        # Save change stub records to rattail database, for consumer thread
        # to find and process.
        saved = 0
        session = Session()
        for key, change in changes:
            for consumer in watcher.consumer_stub_keys:
                session.add(model.DataSyncChange(
                    source=watcher.key,
                    payload_type=change.payload_type,
                    payload_key=change.payload_key,
                    deletion=change.deletion,
                    obtained=now,
                    consumer=consumer))
                saved += 1
            session.flush()
        session.commit()
        session.close()
        log.debug("saved {} '{}' changes to datasync queue".format(saved, watcher.key))
        return True


def prune_changes(watcher, changes):
    """
    Tell the watcher to prune the original change records from its source
    database, if relevant.
    """
    if watcher.prunes_changes:
        try:
            # Note that we only give it the keys for this.
            pruned = watcher.prune_changes([c[0] for c in changes])
        except:
            log.exception("error calling watcher.prune_changes()")
            raise
        else:
            if pruned is not None:
                log.debug("pruned {} changes from '{}' database".format(pruned, watcher.key))


def consume_changes_perpetual(config, profile, consumer):
    """
    Target for DataSync consumer thread.
    """
    # tell consumer to do initial setup
    consumer.setup()

    # begin thread perma-loop
    while True:

        # try to consume all current changes
        if not consume_current_changes(config, profile, consumer):

            # consumption failed, so exit the perma-loop
            # (this thread is now dead)
            break

        # wait 1 sec by default, then look for more changes
        time.sleep(consumer.delay)


def consume_current_changes(config, profile, consumer):
    """
    Consume all changes currently available.
    """
    from rattail.db import Session, model

    session = Session()

    # determine first 'obtained' timestamp
    first = session.query(model.DataSyncChange)\
                   .filter(model.DataSyncChange.source == consumer.watcher.key)\
                   .filter(model.DataSyncChange.consumer == consumer.key)\
                   .order_by(model.DataSyncChange.obtained)\
                   .first()

    error = False
    while first:

        # try to consume these changes
        if not consume_changes_from(config, session, consumer, first.obtained):
            error = True
            break

        else: # fetch next 'obtained' timestamp
            first = session.query(model.DataSyncChange)\
                           .filter(model.DataSyncChange.source == profile.key)\
                           .filter(model.DataSyncChange.consumer == consumer.key)\
                           .order_by(model.DataSyncChange.obtained)\
                           .first()

    # no more changes! (or perhaps an error)
    session.close()
    return not error


def consume_changes_from(config, session, consumer, obtained):
    """
    Consume all changes which were "obtained" at the given timestamp.

    Note that while this function must be given a Rattail database session, the
    function logic is responsible for committing (or rolling back) the session
    transaction.  The assumption here is that this session will be used *only*
    for managing the datasync change queue, and that we should be "saving our
    progress" as changes are fully consumed, i.e. those changes are deleted
    from the queue via session commit.
    """
    from rattail.db import model

    # we only want changes 'obtained' at that time
    changes = session.query(model.DataSyncChange)\
                     .filter(model.DataSyncChange.source == consumer.watcher.key)\
                     .filter(model.DataSyncChange.consumer == consumer.key)\
                     .filter(model.DataSyncChange.obtained == obtained)\
                     .all()

    log.debug("will process %s changes from %s", len(changes),
              localtime(config, obtained, from_utc=True))
    consumer.begin_transaction()

    attempts = 0
    errtype = None
    while True:

        attempts += 1

        try:
            consumer.process_changes(session, changes)
            session.flush()

        except Exception as errobj: # processing failed!
            exc_type, exc, traceback = sys.exc_info()

            consumer.rollback_transaction()
            session.rollback()

            # if we've reached our final attempt, stop retrying
            if attempts >= consumer.retry_attempts:
                log.warning("attempt #%s failed calling `consumer.process_changes()`; "
                            "this thread will now *terminate* until datasync restart",
                            attempts, exc_info=True)
                send_email(config, 'datasync_error_consumer_process_changes', {
                    'watcher': consumer.watcher,
                    'consumer': consumer,
                    'error': exc,
                    'attempts': attempts,
                    'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
                    'datasync_url': config.datasync_url(),
                })
                return False

            # if this exception is not the first, and is of a different type
            # than seen previously, do *not* continue to retry
            if errtype is not None and not isinstance(errobj, errtype):
                log.exception("new exception differs from previous one(s), "
                              "giving up on consumer.process_changes()")
                return False

            # record the type of exception seen; maybe pause before next retry
            errtype = type(errobj)
            log.warning("attempt #%s failed for '%s' -> '%s' consumer.process_changes()",
                        attempts, consumer.watcher.key, consumer.key)
            log.debug("pausing for %s seconds before making attempt #%s of %s",
                      consumer.retry_delay, attempts + 1, consumer.retry_attempts)
            if consumer.retry_delay:
                time.sleep(consumer.retry_delay)

        else: # consumer processed changes okay

            consumer.commit_transaction()

            # delete these changes from datasync queue
            for i, change in enumerate(changes):
                session.delete(change)
                if i % 200 == 0:
                    session.flush()
            session.flush()
            session.commit()

            # can stop the attempt/retry loop now
            log.debug("processed %s changes", len(changes))
            break

    return True
