#!/usr/bin/env python


import os
import sys
import time

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
                   'cores'         : 128, 
                   'gpus'          : 8
                  }
        pdesc   = rp.ComputePilotDescription(pd_init)
        pilot   = pmgr.submit_pilots(pdesc)
        umgr    = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        n    = 1024 * 4
        cuds = list()
        for i in range(0, n):

            cud = rp.ComputeUnitDescription()
            cud.executable       = '/bin/sleep'
            cud.arguments        = ['0']
            cud.gpu_processes    = 0
            cud.cpu_processes    = 1
            cud.cpu_threads      = 1
            cud.cpu_process_type = rp.POSIX
            cud.cpu_thread_type  = rp.POSIX
            cuds.append(cud)

        umgr.submit_units(cuds)
        umgr.wait_units()


        cuds = list()
        for i in range(0, n):

            cud = rp.ComputeUnitDescription()
            cud.executable       = '/bin/sleep'
            cud.arguments        = ['10']
            cud.tag              = 'unit.%06d' % i
            cud.gpu_processes    = 1
            cud.cpu_processes    = 0
            cud.cpu_threads      = 0
            cud.cpu_process_type = rp.POSIX
            cud.cpu_thread_type  = rp.POSIX
            cuds.append(cud)

        umgr.submit_units(cuds)
        umgr.wait_units()


    finally:
        session.close(download=True)


# ------------------------------------------------------------------------------

