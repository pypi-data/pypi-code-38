#!/usr/bin/env python

import os
import sys
import ha_api
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell')
import azure_dbg as dbg

debug_file = "/home/guestshell/azure/HA/azha.log"


def main(argv):
    debug_fh = open(debug_file, "a", os.O_NONBLOCK)
    argc = len(argv)

    if (argc != 2) and (argc < 5):
        dbg.log(debug_fh, 'DBG', "client: set_params: invalid number of arguments %d" % argc)
        debug_fh.close()
        print "Invalid number of arguments %d" % argc 
        ha_api.show_usage(argv[0])
        ha_api.show_azure_usage()
        return 1

    if argv[1] == "-h":
        ha_api.show_usage(argv[0])
        ha_api.show_azure_usage()
        return 0

    (cmd_string, params_dict) = ha_api.make_str_from_args('set_params', sys.argv)

    if cmd_string:
        if not (params_dict.has_key('index')):
            dbg.log(debug_fh, 'DBG', "client: set_param: missing required parameter -i routeIndex")
            debug_fh.close()
            print "Missing required parameter -i routeIndex" 
            ha_api.show_usage(argv[0])
            return 2
        
        debug_fh.close()
        
        req_msg = ha_api.send_command_to_server(cmd_string)
        if req_msg == 'OK':
            rsp_msg = ha_api.get_response_from_server()
            if 'OK' == rsp_msg:
                return 0
            else:
                return 3
        else:
            print req_msg

    else:
        dbg.log(debug_fh, 'ERR', "client: set_params: invalid command syntax %s" % cmd_string)
        debug_fh.close()
        print "Invalid command syntax"
        ha_api.show_usage(argv[0])
        return 4


if __name__ == '__main__':
    sys.exit(main(sys.argv))

  


