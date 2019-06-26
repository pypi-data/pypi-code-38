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
    print "\t-s    to clear the subscriptionId"
    print "\t-g    to clear the resourceGroup"
    print "\t-t    to clear the routeTableName"
    print "\t-n    to clear the nextHopIpAddress"
    print "\t-r    to clear the route"
    print "\t-m    to clear the mode"
    print "\t-a    to clear the applicationId"
    print "\t-d    to clear the tenantId"
    print "\t-k    to clear the applicationKey"
    print "-h prints this help information\n"


def make_str_from_args(command, argv):
    argc = len(argv)

    i = 0
    cmd_string = ''
    params_specified = {}
    for argument in argv:
        token = str(argument)
        if token[0] == '-':
            if token[1] == 'i' :
                index = str(argv[i+1])
                if not index.isdigit():
                    print "Index parameter value (-i) must be a number"
                    return (None, None)
                params_specified['index'] = "YES"
            elif token[1] == 's' :
                params_specified['subscriptionId'] = "YES"
            elif token[1] == 'g' :
                params_specified['resourceGroup'] = "YES"
            elif token[1] == 't' :
                params_specified['routeTable'] = "YES"
            elif token[1] == 'r' :
                params_specified['route'] = "YES"
            elif token[1] == 'n' :
                params_specified['nextHopIpAddr'] = "YES"
            elif token[1] == 'm' :
                params_specified['mode'] = "YES"
            elif token[1] == 'c' :
                params_specified['command'] = "YES"
            elif token[1] == 'a' :
                params_specified['appId'] = "YES"
            elif token[1] == 'd' :
                params_specified['tenantId'] = "YES"
            elif token[1] == 'k' :
                params_specified['appKey'] = "YES"
            elif token[1] == 'h' :
                show_usage(argv[0])
                return (None, None)
            else :
                print "Invalid command option %s" % token[1]
                return (None, None)

        elif i == 0:
            token = command
            
        cmd_string = cmd_string + token + ' '
        i += 1

    return (cmd_string, params_specified)


def main(argv):
    debug_fh = open(debug_file, "a", os.O_NONBLOCK)
    argc = len(argv)

    if (argc != 2) and (argc < 4):
        dbg.log(debug_fh, 'ERR', "client: clear_params: invalid number of arguments %d" % argc)
        debug_fh.close()
        print "Invalid number of arguments %d" % argc 
        show_usage(argv[0])
        return 1

    if argv[1] == "-h":
        show_usage(argv[0])
        return 0

    (cmd_string, params_dict) = make_str_from_args('clear_params', sys.argv)

    if cmd_string:
        if not (params_dict.has_key('index')):
            dbg.log(debug_fh, 'ERR', "client: clear_params: missing required parameter -i routeIndex")
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
        dbg.log(debug_fh, 'ERR', "client: clear_params: invalid command syntax in %s" % cmd_string)
        debug_fh.close()
        print "Invalid syntax in command %s" % cmd_string
        ha_api.show_usage(argv[0])
        return 4


if __name__ == '__main__':
    sys.exit(main(sys.argv))

  


