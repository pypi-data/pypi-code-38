#!/usr/bin/env python

import os
import sys
import ha_api


def show_usage(cmd):
    path = cmd.split('/')
    command = path[-1]
    print "Usage: %s" % command
    print "\t-i <routeIndex>"


def main(argv):
    argc = len(argv)

    if (argc != 3) and (argc != 2):
        err_msg = "Invalid number of arguments %d" % argc
        show_usage(argv[0])
        return err_msg

    if argv[1] == "-h":
        show_usage(argv[0])
        return 

    elif argv[1] != "-i":
        err_msg = "Invalid argument %s" % argv[1]
        show_usage(argv[0])
        return err_msg

    (cmd_string, params_dict) = ha_api.make_str_from_args('show_node', sys.argv)

    if cmd_string:
        if not (params_dict.has_key('index')):
            err_msg = "Missing required parameter -i routeIndex"
            show_usage(argv[0])
            return err_msg
        
        req_msg = ha_api.send_command_to_server(cmd_string)
        if req_msg == 'OK':
            rsp_msg = ha_api.get_response_from_server()
            return rsp_msg
        else:
            print req_msg

    else:
        err_msg = "Invalid syntax"
        show_usage(argv[0])
        return err_msg


if __name__ == '__main__':
    sys.exit(main(sys.argv))

  


