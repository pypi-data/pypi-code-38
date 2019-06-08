#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import sys
import random

import radical.pilot as rp
import radical.utils as ru


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    session = rp.Session()

    try:

        pmgr    = rp.PilotManager(session=session)
        pd_init = {'resource'      : 'local.localhost',
                   'runtime'       : 60,
                   'exit_on_error' : True,
                   'cores'         : '1024'
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        umgr  = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        n = 1024
        cuds = list()
        for i in range(0, n):

            cud = rp.ComputeUnitDescription()
            cud.executable       = '/bin/sleep'
            cud.arguments        = [random.randint(1, 10) * 10]
            cud.gpu_processes    = random.randint(0, 4)
            cud.cpu_processes    = random.randint(1, 8)
            cud.cpu_threads      = random.randint(1, 8)
            cud.gpu_process_type = rp.MPI
            cud.cpu_process_type = rp.MPI
            cud.cpu_thread_type  = rp.POSIX
            cuds.append(cud)

        umgr.submit_units(cuds)
        umgr.wait_units()

    finally:
        session.close(download=True)


# ------------------------------------------------------------------------------

