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

    if argv[1] == "-h":
        ha_api.show_usage(argv[0])
        ha_api.show_azure_usage()
        debug_fh.close()
        return 0

    (cmd_string, params_dict) = ha_api.make_str_from_args('create_node', sys.argv)

    if cmd_string:
        # Check that all the required parameters were provided
        if ((params_dict.has_key('index')) and
            (params_dict.has_key('cloud')) and
            (params_dict.has_key('routeTable'))) :

            if params_dict['index'] == 0:
                dbg.log(debug_fh, 'ERR', "client: create_node: route index of zero is reserved")
                debug_fh.close()
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
            if not (params_dict.has_key('index')):
                print "create_node: missing required parameter -i routeIndex"
                dbg.log(debug_fh, 'ERR', "client: create_node: missing required parameter -i routeIndex")
            if not (params_dict.has_key('cloud')):
                print "create_node: missing required parameter -c cloud"
                dbg.log(debug_fh, 'ERR', "client: create_node: missing required parameter -c cloud")
            if not (params_dict.has_key('routeTable')):
                print "create_node: missing required parameter -t routeTableName"
                dbg.log(debug_fh, 'ERR', "client: create_node: missing required parameter -t routeTableName")
            debug_fh.close()
            ha_api.show_usage(argv[0])
            return 4

    else:
        dbg.log(debug_fh, 'ERR', "client: create_node: invalid command syntax %s" % cmd_string)
        debug_fh.close()
        print "Invalid command syntax %s" % cmd_string
        ha_api.show_usage(argv[0])
        return 5

if __name__ == '__main__':
    sys.exit(main(sys.argv))

  


