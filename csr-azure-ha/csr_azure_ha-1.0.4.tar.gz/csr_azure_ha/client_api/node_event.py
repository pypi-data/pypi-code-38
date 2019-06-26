#!/usr/bin/env python

import os
import sys
import ha_api
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell')
import azure_dbg as dbg

debug_file = "/home/guestshell/azure/HA/azha.log"

def show_usage(cmd):
    path = cmd.split('/')
    command = path[-1]
    print "Usage: %s" % command
    print "\t-i <routeIndex>"
    print "\t-e <eventType>  {peerFail | revert | verify}"
    print "If you set the routeIndex of zero, the event will be applied to all nodes"

def main(argv):
    debug_fh = open(debug_file, "a", os.O_NONBLOCK)
    argc = len(argv)

    if (argc != 2) and (argc != 5) :
        dbg.log(debug_fh, 'ERR', "client: node_event: invalid number of arguments %d" % argc)
        debug_fh.close()
        print "Invalid number of arguments %d" % argc
        show_usage(argv[0])
        return 1

    if argv[1] == "-h":
        show_usage(argv[0])
        debug_fh.close()
        return 0
    elif argv[1] != "-i":
        dbg.log(debug_fh, 'ERR', "client: node_event: invalid argument %d" % argv[1])
        debug_fh.close()
        print "Invalid argument %s" % argv[1]
        show_usage(argv[0])
        return 2
    elif argv[3] != "-e":
        dbg.log(debug_fh, 'ERR', "client: node_event: invalid argument %d" % argv[3])
        debug_fh.close()
        print "Invalid argument %s" % argv[3]
        show_usage(argv[0])
        return 3
    elif ((argv[4] != 'peerFail') and 
          (argv[4] != 'revert') and
          (argv[4] != 'verify') ):
        dbg.log(debug_fh, 'ERR', "client: node_event: invalid event type %s" % argv[4])
        debug_fh.close()
        print "Invalid event type %s" % argv[4]
        show_usage(argv[0])
        return 4

    (cmd_string, params_dict) = ha_api.make_str_from_args('node_event', sys.argv)

    if cmd_string:
        if not (params_dict.has_key('index')):
            dbg.log(debug_fh, 'ERR', "client: node_event: missing required parameter -i routeIndex")
            debug_fh.close()
            print "Missing required parameter -i routeIndex"
            show_usage(argv[0])
            return 5

        if not (params_dict.has_key('eventType')):
            dbg.log(debug_fh, 'ERR', "client: node_event: missing required parameter -e eventType")
            debug_fh.close()
            print "Missing required parameter -e eventType"
            show_usage(argv[0])
            return 6

        debug_fh.close()
        
        req_msg = ha_api.send_command_to_server(cmd_string)
        if req_msg == 'OK':
            rsp_msg = ha_api.get_response_from_server()
            if 'OK' == rsp_msg:
                return 0
            else:
                return 7
        else:
            print req_msg
 
    else:
        dbg.log(debug_fh, 'ERR', "client: create_node: invalid command syntax %s" % cmd_string)
        debug_fh.close()
        print "Invalid command syntax %s" % cmd_string
        show_usage(argv[0])
        return 8

        
if __name__ == '__main__':
    sys.exit(main(sys.argv))

  


