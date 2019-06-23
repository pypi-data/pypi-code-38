#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT: a XMPP client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""tools related to deferred"""

from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from twisted.internet import defer
from twisted.internet import error as internet_error
from twisted.internet import reactor
from twisted.words.protocols.jabber import error as jabber_error
from twisted.python import failure
from sat.core.constants import Const as C
from sat.memory import memory

KEY_DEFERREDS = "deferreds"
KEY_NEXT = "next_defer"


def stanza2NotFound(failure_):
    """Convert item-not-found StanzaError to exceptions.NotFound"""
    failure_.trap(jabber_error.StanzaError)
    if failure_.value.condition == u'item-not-found':
        raise exceptions.NotFound(failure_.value.text or failure_.value.condition)
    return failure_


class DelayedDeferred(object):
    """A Deferred-like which is launched after a delay"""

    def __init__(self, delay, result):
        """
        @param delay(float): delay before launching the callback, in seconds
        @param result: result used with the callback
        """
        self._deferred = defer.Deferred()
        self._timer = reactor.callLater(delay, self._deferred.callback, result)

    def cancel(self):
        try:
            self._timer.cancel()
        except internet_error.AlreadyCalled:
            pass
        self._deferred.cancel()

    def addCallbacks(self, *args, **kwargs):
        self._deferred.addCallbacks(*args, **kwargs)

    def addCallback(self, *args, **kwargs):
        self._deferred.addCallback(*args, **kwargs)

    def addErrback(self, *args, **kwargs):
        self._deferred.addErrback(*args, **kwargs)

    def addBoth(self, *args, **kwargs):
        self._deferred.addBoth(*args, **kwargs)

    def chainDeferred(self, *args, **kwargs):
        self._deferred.chainDeferred(*args, **kwargs)

    def pause(self):
        self._deferred.pause()

    def unpause(self):
        self._deferred.unpause()


class RTDeferredSessions(memory.Sessions):
    """Real Time Deferred Sessions"""

    def __init__(self, timeout=120):
        """Manage list of Deferreds in real-time, allowing to get intermediate results

        @param timeout (int): nb of seconds before deferreds cancellation
        """
        super(RTDeferredSessions, self).__init__(
            timeout=timeout, resettable_timeout=False
        )

    def newSession(self, deferreds, profile):
        """Launch a new session with a list of deferreds

        @param deferreds(list[defer.Deferred]): list of deferred to call
        @param profile: %(doc_profile)s
        @param return (tupe[str, defer.Deferred]): tuple with session id and a deferred wich fire *WITHOUT RESULT* when all results are received
        """
        data = {KEY_NEXT: defer.Deferred()}
        session_id, session_data = super(RTDeferredSessions, self).newSession(
            data, profile=profile
        )
        if isinstance(deferreds, dict):
            session_data[KEY_DEFERREDS] = deferreds.values()
            iterator = deferreds.iteritems()
        else:
            session_data[KEY_DEFERREDS] = deferreds
            iterator = enumerate(deferreds)

        for idx, d in iterator:
            d._RTDeferred_index = idx
            d._RTDeferred_return = None
            d.addCallback(self._callback, d, session_id, profile)
            d.addErrback(self._errback, d, session_id, profile)
        return session_id

    def _purgeSession(
        self, session_id, reason=u"timeout", no_warning=False, got_result=False
    ):
        """Purge the session

        @param session_id(str): id of the session to purge
        @param reason (unicode): human readable reason why the session is purged
        @param no_warning(bool): if True, no warning will be put in logs
        @param got_result(bool): True if the session is purged after normal ending (i.e.: all the results have been gotten).
            reason and no_warning are ignored if got_result is True.
        @raise KeyError: session doesn't exists (anymore ?)
        """
        if not got_result:
            try:
                timer, session_data, profile = self._sessions[session_id]
            except ValueError:
                raise exceptions.InternalError(
                    u"was expecting timer, session_data and profile; is profile set ?"
                )

            # next_defer must be called before deferreds,
            # else its callback will be called by _gotResult
            next_defer = session_data[KEY_NEXT]
            if not next_defer.called:
                next_defer.errback(failure.Failure(defer.CancelledError(reason)))

            deferreds = session_data[KEY_DEFERREDS]
            for d in deferreds:
                d.cancel()

            if not no_warning:
                log.warning(
                    u"RTDeferredList cancelled: {} (profile {})".format(reason, profile)
                )

        super(RTDeferredSessions, self)._purgeSession(session_id)

    def _gotResult(self, session_id, profile):
        """Method called after each callback or errback

        manage the next_defer deferred
        """
        session_data = self.profileGet(session_id, profile)
        defer_next = session_data[KEY_NEXT]
        if not defer_next.called:
            defer_next.callback(None)

    def _callback(self, result, deferred, session_id, profile):
        deferred._RTDeferred_return = (True, result)
        self._gotResult(session_id, profile)

    def _errback(self, failure, deferred, session_id, profile):
        deferred._RTDeferred_return = (False, failure)
        self._gotResult(session_id, profile)

    def cancel(self, session_id, reason=u"timeout", no_log=False):
        """Stop this RTDeferredList

        Cancel all remaining deferred, and call self.final_defer.errback
        @param reason (unicode): reason of the cancellation
        @param no_log(bool): if True, don't log the cancellation
        """
        self._purgeSession(session_id, reason=reason, no_warning=no_log)

    def getResults(
        self, session_id, on_success=None, on_error=None, profile=C.PROF_KEY_NONE
    ):
        """Get current results of a real-time deferred session

        result already gotten are deleted
        @param session_id(str): session id
        @param on_success: can be:
            - None: add success normaly to results
            - callable: replace result by the return value of on_success(result) (may be deferred)
        @param on_error: can be:
            - None: add error normaly to results
            - C.IGNORE: don't put errors in results
            - callable: replace failure by the return value of on_error(failure) (may be deferred)
        @param profile=%(doc_profile)s
        @param result(tuple): tuple(remaining, results) where:
            - remaining[int] is the number of remaining deferred
                (deferreds from which we don't have result yet)
            - results is a dict where:
                - key is the index of the deferred if deferred is a list, or its key if it's a dict
                - value = (success, result) where:
                    - success is True if the deferred was successful
                    - result is the result in case of success, else the failure
            If remaining == 0, the session is ended
        @raise KeyError: the session is already finished or doesn't exists at all
        """
        if profile == C.PROF_KEY_NONE:
            raise exceptions.ProfileNotSetError
        session_data = self.profileGet(session_id, profile)

        @defer.inlineCallbacks
        def next_cb(__):
            # we got one or several results
            results = {}
            filtered_data = []  # used to keep deferreds without results
            deferreds = session_data[KEY_DEFERREDS]

            for d in deferreds:
                if (
                    d._RTDeferred_return
                ):  # we don't use d.called as called is True before the full callbacks chain has been called
                    # we have a result
                    idx = d._RTDeferred_index
                    success, result = d._RTDeferred_return
                    if success:
                        if on_success is not None:
                            if callable(on_success):
                                result = yield on_success(result)
                            else:
                                raise exceptions.InternalError(
                                    "Unknown value of on_success: {}".format(on_success)
                                )

                    else:
                        if on_error is not None:
                            if on_error == C.IGNORE:
                                continue
                            elif callable(on_error):
                                result = yield on_error(result)
                            else:
                                raise exceptions.InternalError(
                                    "Unknown value of on_error: {}".format(on_error)
                                )
                    results[idx] = (success, result)
                else:
                    filtered_data.append(d)

            # we change the deferred with the filtered list
            # in other terms, we don't want anymore deferred from which we have got the result
            session_data[KEY_DEFERREDS] = filtered_data

            if filtered_data:
                # we create a new next_defer only if we are still waiting for results
                session_data[KEY_NEXT] = defer.Deferred()
            else:
                # no more data to get, the result have been gotten,
                # we can cleanly finish the session
                self._purgeSession(session_id, got_result=True)

            defer.returnValue((len(filtered_data), results))

        # we wait for a result
        return session_data[KEY_NEXT].addCallback(next_cb)
