#!/usr/bin/env python

import sys
import time

import radical.pilot as rp


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    times   = list()
    session = None
    n       = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    try:

        times.append(time.time())
        session = rp.Session()
        pmgr    = rp.PilotManager(session=session)
        umgr    = rp.UnitManager(session=session)

        times.append(time.time())
        times.append(time.time())
      # pd_init = {'resource'      : 'local.localhost',
      #            'runtime'       : 20,
      #            'exit_on_error' : True,
      #            'cores'         : 160
      #           }
        pd_init = {'resource'      : 'ornl.titan_aprun',
                   'project'       : 'BIP149',
                   'queue'         : 'debug',
                   'runtime'       : 20,
                   'exit_on_error' : True,
                   'cores'         : 160
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        umgr.add_pilots(pilot)
        times.append(time.time())

        pmgr.wait_pilots(state=[rp.PMGR_ACTIVE])
        times.append(time.time())

        cuds = list()
        for i in range(0, n):
            cud = rp.ComputeUnitDescription()
          # cud.executable       = '/bin/true'
            cud.executable       = '/bin/sh'
            cud.arguments        = 'gromacs/gromacs.sh'
            cud.input_staging    = [{'source': 'client:///gromacs', 
                                     'target': 'unit:///gromacs',
                                     'action': rp.TARBALL}]
            cud.cpu_processes    = 1
            cuds.append(cud)
        umgr.submit_units(cuds)
        times.append(time.time())

        umgr.wait_units()
        times.append(time.time())

        pilot.cancel()
        times.append(time.time())


    finally:
        if session:
            session.close()

    times.append(time.time())
    data = '%6d \t %s\n' % (n, ''.join(['\t%6.2f' % (t - times[0]) 
                                        for t in times]))
    with open('rp.dat', 'a+') as fout:
        print data
        fout.write(data)

# ------------------------------------------------------------------------------

