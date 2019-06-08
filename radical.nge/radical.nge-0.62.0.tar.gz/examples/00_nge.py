#!/usr/bin/env python

import sys
import time

import radical.pilot as rp
import radical.nge   as rn

tgt = 'titan'
tgt = 'local'

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 32

    unum  = n
    ugen  = 2    # generations
    usize = 4    # threads
    utime = 1    # sec
    psize = int(n * usize / ugen)

    nge = None
    sid = None
    url = 'http://guest:guest@localhost:8090/'

    try:
        print 'connect'
        nge = rn.NGE_RS(url=url, sid=sid)

        print 'check_session'
        sid = nge.session()
        print 'sid: %s' % sid

        print 'list_sessions'
        print nge.list_sessions()
        
        sid = 'foo.1'
        print 'start_session %s' % sid
        nge.session(sid)

        print 'check_session'
        print 'sid: %s' % nge.session()


      # print 'request backfill resources'
      # pprint.pprint(nge.request_backfill_resources(
      #                                    {'resource' : 'ornl.titan_aprun',
      #                                     'queue'    : 'debug',
      #                                     'project'  : "CSC230"},
      #                                    partition='titan',
      #                                    policy='default'))
      # print 'ok'
      #
      # print 'inspect resources'
      # print nge.list_resources()
      # print 'ok'

        print 'request resources'
        if tgt == 'titan':
            print nge.request_resources([{'resource' : 'ornl.titan_aprun',
                                          'queue'    : 'debug',
                                          'project'  : 'BIP149',
                                          'cores'    : psize + 16*1,  # agent nodes
                                          'walltime' : 60}])
        else:
            print nge.request_resources([{'resource' : 'local.localhost',
                                          'cores'    : 160,
                                          'walltime' : 20}])
        print 'ok'

#       print 'inspect resources'
#       print nge.list_resources()
#       print 'ok'
#
#       print 'find resources'
#       print nge.find_resources()
#       print 'ok'
#
#       print 'get_requested_resources'
#       print nge.get_requested_resources()
#       print 'ok'
#
#       print 'get_available_resources'
#       print nge.get_available_resources()
#       print 'ok'
#
#       print 'get_resource_info'
#       print nge.get_resource_info()
#       print 'ok'
#
#       print 'get_resource_states'
#       print nge.get_resource_states()
#       print 'ok'

        print 'wait_resource_states'
        print nge.wait_resource_states(states=rp.PMGR_ACTIVE)
        print 'ok'

        sys.exit(0)


    finally:
        if nge:
            pass
          # print 'logout'
          # nge.logout()
          # print 'ok'
          # raise


# ------------------------------------------------------------------------------

