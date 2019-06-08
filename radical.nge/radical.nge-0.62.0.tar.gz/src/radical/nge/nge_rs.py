
__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__   = "MIT"

import os
import json
import time
import pprint
import requests

import radical.utils as ru


# --------------------------------------------------------------------------
#
class NGE_RS(object):
    '''
    This is class interfaces to the NGE service's REST API.
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self, url, sid=None, log=None, rep=None, prof=None):

        if log : self._log  = log
        else   : self._log  = ru.Logger('radical.nge')

        if rep : self._rep  = log
        else   : self._rep  = ru.Reporter('radical.nge')

        if prof: self._prof = prof
        else   : self._prof = ru.Profiler('radical.nge')

        self._cookies        = list()
        self._url            = ru.Url(url)
        self._qbase          = ru.Url(url)
        self._qbase.username = ''
        self._qbase.password = ''
        self._qbase          = str(self._qbase)
        self._qbase          = self._qbase.rstrip('/')

        if self._url.username and self._url.password:
            self.login(self._url.username, self._url.password)

        if sid:
            self.connect_session(sid)


    # --------------------------------------------------------------------------
    #
    def _query(self, mode, route, data=None):

        url = self._qbase + route
        print '---> %s' % url

        self._log.debug('request %5s: %s [%s]', mode, route, data)
        self._log.debug('request %5s: %s', mode, url)

        if mode == 'get':
            r = requests.get(url, cookies=self._cookies)

        elif mode == 'put':
            r = requests.put(url, cookies=self._cookies, json=data)

        else:
            raise ValueError('invalid query mode %s' % mode)

        self._log.debug('reply   %3s: %s [%s]', r.status_code,
                                                 len(r.content), r.content[:64])

        if r.status_code != 200:
            raise RuntimeError('query failed:\n %s' % r.content)

        if r.cookies:
            assert(not self._cookies), 'we allow auth only once'
            self._cookies = r.cookies

        try:
            result = json.loads(r.content)

        except ValueError as e:
            raise RuntimeError('query failed: %s' % repr(e))

        if not result['success']:
            raise RuntimeError('query failed: %s' % result['error'])

        return result['result']



    # --------------------------------------------------------------------------
    #
    def login(self, username, password):
        '''
        login to the service with given username and password.  This method will
        stor a cookie with a session secret so that future calls on this NGE
        object instance use the same credentials.  Another call to `login` will
        overwrite that cookie and use the new credentials.
        '''

        data = {'username' : self._url.username, 
                'password' : self._url.password}

        return self._query('put', '/login/', data=data)


    # --------------------------------------------------------------------------
    #
    def session(self, sid=None):
        '''
        check if the named session exists.  If not, the session is created.
        If sid is None, then no session is connected or created.

        The method will return the sid of the currently active session
        (or `None` if no session is active).
        '''

        data = {'sid': sid}

        return self._query('put', '/session/', data=data)


    # --------------------------------------------------------------------------
    #
    def list_sessions(self):
        '''
        return all session IDs known for this user (irrespective of session
        state)
        '''

        return self._query('get', '/sessions/')


    # --------------------------------------------------------------------------
    #
    def request_backfill_resources(self, request_stub, partition, policy):
        '''
        request resources as backfill jobs.
        '''

        return self._query('put', '/resources/backfill/%s/%s/' % 
                           (partition, policy), data=request_stub)


    # --------------------------------------------------------------------------
    #
    def request_resources(self, requests):
        '''
        request a new resource (ie. submit a new RP pilot) for a given set of
        cores / walltime.
        '''

        if   not requests                  : requests = list()
        elif not isinstance(requests, list): requests = [requests]

        return self._query('put', '/resources/', data=requests)


    # --------------------------------------------------------------------------
    #
    def list_resources(self):
        '''
        return the UIDs for all known resources (ie. RP pilots), independent of
        their state.
        '''

        return self._query('get', '/resources/')


    # --------------------------------------------------------------------------
    #
    def find_resources(self, states=None):
        '''
        return the UIDs for all known resources (ie. RP pilots) in the given
        states, or in any state if no state filter is defined.
        '''

        if   not states                  : states = list()
        elif not isinstance(states, list): states = [states]

        ret  = list()
        rids = self.list_resources()

        states = self.get_resource_states(rids)
        for rid,state in zip(rids, states):
            if state in states:
                ret.append(rid)

        return ret


    # --------------------------------------------------------------------------
    #
    def get_resource_info(self, resource_ids=None):
        '''
        get information for all resources (ie. RP pilots) with the given UIDs
        (or for all known resources if no UID is specified).
        '''

        if not resource_ids:
            resource_ids = self.list_resources()
        elif not isinstance(resource_ids, list): 
            resource_ids = [resource_ids]

        ret = list()
        for rid in resource_ids:

            info = self._query('get', '/resources/%s/info' % rid)
            ret.append(info)

        return ret


    # --------------------------------------------------------------------------
    #
    def get_requested_resources(self):
        '''
        find all resources (ie. pilots) in *any* state, and return number of
        cores, walltime and state as tuples.
        '''

        return self._query('get', '/resources/requested')


    # --------------------------------------------------------------------------
    #
    def get_available_resources(self):
        '''
        find all `ACTIVE` resources (ie. pilots) and return number of cores,
        walltime and state as tuples.
        '''

        return self._query('get', '/resources/available')


    # --------------------------------------------------------------------------
    #
    def get_resource_states(self, resource_ids=None):
        '''
        get the state for all resources (ie. RP pilots) with the given UIDs
        (or for all known resources if no UID is specified).
        '''

        if not resource_ids:
            resource_ids = self.list_resources()
        elif not isinstance(resource_ids, list):
            resource_ids = [resource_ids]

        ret = list()
        for rid in resource_ids:

            state = self._query('get', '/resources/%s/state' % rid)
            ret.append(state)

        return ret


    # --------------------------------------------------------------------------
    #
    def wait_resource_states(self, resource_ids=None, 
                             states=None, timeout=None):
        '''
        wait for a specific (set of) states for all resources (ie. RP pilots)
        with the given UIDs (or for all known resources if no UID is specified).
        This call will return after a given timeout, or after the states have
        been reached, whichever occurs first.  A negative timeout value will
        cause it to wait forever.
        '''

        if not isinstance(states, list): states = [states]
        else:
            pass
          # raise NotImplementedError('can only wait for one state')

        state = states[0]

        # FIXME: this is state model agnostic - passed states will never be
        #        matched
        if not resource_ids:
            resource_ids = self.list_resources()
        elif not isinstance(resource_ids, list):
            resource_ids = [resource_ids]

        for rid in resource_ids:

            self._query('get', '/resources/%s/wait/%s/%s' % (rid, state, timeout))

        return


    # --------------------------------------------------------------------------
    #
    def cancel_resources(self, resource_ids=None):
        '''
        cancel all resources (ie. RP pilots) with the given UIDs (or for all
        known resources if no UID is specified).  This call will return when the
        resource states are final.
        '''

        # FIXME: this is state model agnostic - passed states will never be
        #        matched
        if not resource_ids:
            resource_ids = self.list_resources()
        elif not isinstance(resource_ids, list):
            resource_ids = [resource_ids]

        for rid in resource_ids:

            self._query('get', '/resources/%s/cancel' % (rid))

        return


    # --------------------------------------------------------------------------
    #
    def submit_tasks(self, descriptions):
        '''
        Harvester task descriptions are submitted to the RP level resources
        (pilots).
        '''

        if   not descriptions                  : descriptions = list()
        elif not isinstance(descriptions, list): descriptions = [descriptions]

        return self._query('put', '/tasks/', data=descriptions)


    # --------------------------------------------------------------------------
    #
    def list_tasks(self):
        '''
        return UIDs for all known tasks (ie. RP units)
        '''

        return self._query('get', '/tasks/')


    # --------------------------------------------------------------------------
    #
    def get_task_states(self, task_ids=None):
        '''
        return states for the tasks (ie. RP units) with the given UIDs, or for
        all tasks, if no UIDs are specified
        '''

        if task_ids:

            if not isinstance(task_ids, list):
                task_ids = [task_ids]

            ret = list()
            for tid in task_ids:
                state = self._query('get', '/tasks/%s/state' % tid)
                ret.append(state)
        else:
            ret = self._query('get', '/tasks/state')

        return ret


    # --------------------------------------------------------------------------
    #
    def wait_task_states(self, task_ids=None, states=None, timeout=None):
        '''
        wait for a specific (set of) states for all tasks (ie. RP units)
        with the given UIDs (or for all known tasks if no UID is specified).
        This call will return after a given timeout, or after the states have
        been reached, whichever occurs first.  A negative timeout value will
        cause it to wait forever.
        '''

        if not states:
            state = ''

        else:
            if not isinstance(states, list): states = [states]
            else:
                pass  # raise NotImplementedError('can only wait for one state')
            state = states[0]

        if not timeout:
            # FIXME: we should do those conversions in `self._query`
            timeout = '0'

        if task_ids:
            if not isinstance(task_ids, list):
                task_ids = [task_ids]
            for tid in task_ids:
                self._query('get', '/tasks/%s/wait/%s/%s' % (tid, state, timeout))
        else:
            self._query('get', '/tasks/wait/%s/%s' % (state, timeout))

        return


# ------------------------------------------------------------------------------

