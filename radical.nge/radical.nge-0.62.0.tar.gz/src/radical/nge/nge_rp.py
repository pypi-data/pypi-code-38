
__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__   = "MIT"


import time

import radical.pilot as rp

from .utils import get_backfill


MAX_CORES    = 160  # 10 nodes on titan
MAX_WALLTIME =  60  #  1 hour == debug on titan


# --------------------------------------------------------------------------
#
class NGE_RP(object):
    '''
    This class interfaces from a NGE_RS like API to radical.pilot
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self, log=None, rep=None, prof=None):

        if log : self._log  = log
        else   : self._log  = ru.Logger('radical.nge')

        if rep : self._rep  = log
        else   : self._rep  = ru.Reporter('radical.nge')

        if prof: self._prof = prof
        else   : self._prof = ru.Profiler('radical.nge')

        self._session = rp.Session()
        self._pmgr    = rp.PilotManager(self._session)
        self._umgr    = rp.UnitManager(self._session)

        self._umgr.register_callback(self._unit_state_cb)


    # --------------------------------------------------------------------------
    #
    @property
    def uid(self):

        return self._session.uid


    # --------------------------------------------------------------------------
    #
    def close(self):

        self._session.close(download=True)


    # --------------------------------------------------------------------------
    #
    def request_backfill_resources(self, request_stub, partition, policy):
        '''
        Request new backfill resources, chunked by the given max_cores and
        max_walltime.  The given request_stub is used as template for the pilot
        descriptions.
        '''

        max_cores    = policy.get('max_cores'   , MAX_CORES   )
        max_walltime = policy.get('max_walltime', MAX_WALLTIME)

        self._rep.header('request resources tasks\n')
        self._rep.info('\nrequesting backfill resources\n')
        bf = get_backfill(partition, max_cores, max_walltime)

      # print 'bf list:'
      # import pprint
      # pprint.pprint(bf)

        pds = list()
        for [partition, cores, walltime] in bf:
            pd = {'resource': request_stub.get('resource', 'local.localhost'),
                  'project' : request_stub.get('project'),
                  'queue'   : request_stub.get('queue'),
                  'cores'   : cores, 
                  'runtime' : walltime
                 }
            self._rep.ok('backfill  on %s [%5dcores * %4dmin] @ %10s(%10s)]\n' %
                         (pd['resource'], pd['cores'], pd['runtime'],
                          pd['queue'], pd['project']))
          # pprint.pprint(pd)
            pds.append(rp.ComputePilotDescription(pd))

        pilots = self._pmgr.submit_pilots(pds)
        self._umgr.add_pilots(pilots)


    # --------------------------------------------------------------------------
    #
    def request_resources(self, requests):
        '''
        request a new resource (ie. submit a new RP pilot) for a given set of
        cores / walltime.
        '''

        self._rep.header('request resources tasks\n')
        self._rep.info('\nrequesting dedicated resources\n')
        pds = list()
        for request in requests:
            pd  = {'resource' : request.get('resource', 'local.localhost'),
                    'project' : request.get('project'),
                    'queue'   : request.get('queue'),
                    'cores'   : request['cores'],
                    'runtime' : request['walltime']
                  }
            self._rep.ok('provision on %s [%5dcores * %4dmin] @ %10s(%10s)]\n' %
                         (pd['resource'], pd['cores'], pd['runtime'],
                          pd['queue'], pd['project']))
            pds.append(rp.ComputePilotDescription(pd))

        pilots = self._pmgr.submit_pilots(pds)
        self._umgr.add_pilots(pilots)

        return [p.uid for p in pilots]


    # --------------------------------------------------------------------------
    #
    def list_resources(self):

        self._rep.info('\nresource listing\n')
        [self._rep.ok('%s\n' % pilot.uid) for pilot in self._pmgr.get_pilots()]

        return [pilot.uid for pilot in self._pmgr.get_pilots()]


    # --------------------------------------------------------------------------
    #
    def find_resources(self, states=None):

        if   not states                  : states = list()
        elif not isinstance(states, list): states = [states]

        self._rep.info('\nresource query (%s)\n' % states)
        [self._rep.ok('%s\n' % pilot.uid) for pilot in self._pmgr.get_pilots()]
        ret = list()
        if states:
            for pilot in self._pmgr.get_pilots():
                if pilot.state in states:
                    ret.append(pilot.uid)
        else:
            ret = self._pmgr.list_pilots()

        return ret


    # --------------------------------------------------------------------------
    #
    def get_requested_resources(self):

        self._rep.info('\nresource info query\n')

        ret = list()
        for info in self.get_resource_info():
            ret.append([info['uid'], info['state'], 
                        info['description']['cores'], 
                        info['description']['runtime']
                      ])
            self._rep.ok('%s: %10s [%5dcores * %4dmin]\n' % 
                         (info['uid'], info['state'],
                          info['description']['cores'], 
                          info['description']['runtime']))
        return ret


    # --------------------------------------------------------------------------
    #
    def get_available_resources(self):

        self._rep.info('\nresource info query (active)\n')

        ret = list()
        for info in self.get_resource_info():
            if info['state'] == rp.PMGR_ACTIVE:
                ret.append([info['uid'], info['state'], 
                            info['description']['cores'], 
                            info['description']['runtime']
                           ])
                self._rep.ok('%s: %10s [%5dcores * %4dmin]\n' % 
                             (info['uid'], info['state'],
                              info['description']['cores'], 
                              info['description']['runtime']))
        return ret


    # --------------------------------------------------------------------------
    #
    def get_resource_info(self, resource_ids=None):

        if   not resource_ids                  : resource_ids = list()
        elif not isinstance(resource_ids, list): resource_ids = [resource_ids]

        ret = list()
        if resource_ids:

            pilots = self._pmgr.get_pilots()

            if   not pilots                  : pilots = list()
            elif not isinstance(pilots, list): pilots = [pilots]

            for pilot in pilots:
                if pilot.uid in resource_ids:
                    ret.append(pilot.as_dict())
        else:
            for pilot in self._pmgr.get_pilots():
                ret.append(pilot.as_dict())

        return ret


    # --------------------------------------------------------------------------
    #
    def get_resource_states(self, resource_ids=None):

        self._rep.info('\nresource state query\n')
        pilots = self._pmgr.get_pilots(resource_ids)

        if   not pilots                  : pilots = list()
        elif not isinstance(pilots, list): pilots = [pilots]

        for pilot in pilots:
            self._rep.ok('%s: %10s\n' % (pilot.uid, pilot.state))
        return [pilot.state for pilot in pilots]


    # --------------------------------------------------------------------------
    #
    def wait_resource_states(self, resource_ids=None, 
                             states=None, timeout=None):

        self._rep.info('\nwait for resource\n')
        return self._pmgr.wait_pilots(uids=resource_ids, state=states,
                                      timeout=timeout)


    # --------------------------------------------------------------------------
    #
    def cancel_resources(self, resource_ids=None):

        self._rep.info('\ncancel resources query\n')
        pilots = self._pmgr.get_pilots(resource_ids)

        self._pmgr.cancel_pilots(resource_ids)
        self._pmgr.wait_pilots  (resource_ids, rp.FINAL)

        if   not pilots                  : pilots = list()
        elif not isinstance(pilots, list): pilots = [pilots]

        for pilot in pilots:
            self._rep.ok('%s: %10s\n' % (pilot.uid, pilot.state))

        return [pilot.state for pilot in pilots]


    # --------------------------------------------------------------------------
    #
    def submit_tasks(self, descriptions):

        # FIXME: we actually get PANDA task descriptions here, which we need to
        #        translate into RP unit descriptions

        # before we hand over tasks to the RP layer, we will stage files
        # FIXME: panda level input file staging goes here.

        self._rep.header('submit tasks\n')
        cuds = list()
        for descr in descriptions:
            cuds.append(rp.ComputeUnitDescription(descr))

        units = self._umgr.submit_units(cuds)

        return [unit.uid for unit in units]


    # --------------------------------------------------------------------------
    #
    def _unit_state_cb(self, unit, state):

        # once the units are in final state, we can run the panda output staging
        # routines.  To learn about final units, we registered this unit state
        # callback.on umgr creation.
        if state == rp.DONE:
          # self._rep.ok('task completed %s\n' % unit.uid)
            pass
            # FIXME: panda level output file staging goes here.
            # FIXME: we need to make sure that PANDA is informed when our output
            #        staging is done, and when the units can be controlled by
            #        the panda layer again.  For that, we will set
            #            'control': 'panda_pending'
            #        in the unit dict returned to Panda on inspection, to signal
            #        that control is relinguished.  Note that `DONE` is
            #        insufficient, precisely because of the additional output
            #        staging.
            # NOTE:  can we translate the panda staging into proper RP staging
            #        directives, to avoid explicit control management?
        elif state == rp.FAILED:
          # self._rep.error('task failed    %s\n' % unit.uid)
            pass


    # --------------------------------------------------------------------------
    #
    def list_tasks(self):

        return self._umgr.list_units()


    # --------------------------------------------------------------------------
    #
    def get_task_states(self, task_ids=None):

        if task_ids:
            if not isinstance(task_ids, list):
                task_ids = [task_ids]

        units = self._umgr.get_units(task_ids)

        if   not units:                   units = list()
        elif not isinstance(units, list): units = [units]

        return [unit.state for unit in units]


    # --------------------------------------------------------------------------
    #
    def wait_task_states(self, task_ids=None, states=None, timeout=None):

        return self._umgr.wait_units(uids=task_ids, state=states,
                                     timeout=timeout)


# ------------------------------------------------------------------------------

