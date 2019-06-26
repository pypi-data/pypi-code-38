#!/usr/bin/env python

import sys
import os
import time
import socket
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_ha/client_api')
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_ha/server')
import ha_server
import azure_dbg as dbg

sock_file = "/home/guestshell/azure/HA/sock_file"
debug_file = "/home/guestshell/azure/HA/azha.log"


def show_usage(cmd):
    path = cmd.split('/')
    command = path[-1]
    print "Usage: %s" % command
    print "\t-i <routeIndex>       (1..256)"
    print "\t-p <cloud_provider>   {azure | azusgov}"
    print "\t-s <subscriptionId>"
    print "\t-g <resourceGroup>"
    print "\t-t <routeTableName>"
    print "\t-n <nextHopIpAddress>"
    print "\t-r <route>   e.g. 15.0.0.0/8"
    print "\t-m <mode>  {primary | secondary}"
    print "The route parameter is optional. If excluded, all the routes in the specified route table will be updated."
    print "The mode parameter is optional. If excluded the mode is assumed to be secondary."
    print "-h prints this help information\n"

def show_azure_usage():
    print "Azure specific options:"
    print "\t-a <applicationId>"
    print "\t-d <tenantId>"
    print "\t-k <applicationKey>"
    print "These options are only required when using Azure Active Directory for authentication. If using Managed Services Identity to authenticate, these parameters should be excluded."


def show_api_usage():
    print "Usage: ha_api -c {start | stop | ping}"


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
            elif token[1] == 'c' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['command'] = "YES"
            elif token[1] == 'p' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['cloud'] = "YES"
            elif token[1] == 's' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['subscriptionId'] = "YES"
            elif token[1] == 'g' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['resourceGroup'] = "YES"
            elif token[1] == 't' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['routeTable'] = "YES"
            elif token[1] == 'r' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['route'] = "YES"
            elif token[1] == 'n' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['nextHopIpAddress'] = "YES"
            elif token[1] == 'm' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['mode'] = "YES"
            elif token[1] == 'a' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['appId'] = "YES"
            elif token[1] == 'd' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['tenantId'] = "YES"
            elif token[1] == 'k' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['appKey'] = "YES"
            elif token[1] == 'e' :
                if argv[i+1][0] == '-' :
                    print "Missing value for parameter %s" % token
                    return (None, None)
                params_specified['eventType'] = "YES"

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


def send_command_to_server(command):
    global sock, debug_fh

    # Open up a file to write error and debug messages
    debug_fh = open(debug_file, "a", os.O_NONBLOCK)

    # Create a UDS socket and connect the socket to the port where
    # the server is listening
    for attempt in range(1, 4):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(sock_file)
            sock.sendall(command)
            sock.shutdown(socket.SHUT_WR)
            return 'OK'

        except socket.error as err:
            dbg.log(debug_fh, 'ERR', "API: socket error %s errno=%d" % (err, err.errno))
            if attempt < 3:
                dbg.log(debug_fh, 'ERR', "%s failed on attempt %d" % (command, attempt))
                time.sleep(2)
            else:
                dbg.log(debug_fh, 'ERR', "%s failed" % command)
                return "%s failed" % command
        except socket.timeout:
            dbg.log(debug_fh, 'ERR', "API: socket timeout")
            if attempt < 3:
                dbg.log(debug_fh, 'ERR', "%s failed on attempt %d" % (command, attempt))
                time.sleep(2)
            else:
                dbg.log(debug_fh, 'ERR', "%s failed" % command)
                return "%s failed" % command
        except Exception as err:
            dbg.log(debug_fh, 'ERR', "API: other socket error %s" % err)
            if attempt < 3:
                dbg.log(debug_fh, 'ERR', "%s failed on attempt %d" % (command, attempt))
                time.sleep(2)
            else:
                dbg.log(debug_fh, 'ERR', "%s failed" % command)
                return "%s failed" % command


def get_response_from_server():
    try:
        rsp_msg = sock.recv(512)
        debug_fh.close()
        sock.close()
        return rsp_msg
    except socket.error as err:
        dbg.log(debug_fh, 'ERR', "API: socket error %s errno=%d" % (err, err.errno))
        return "API: socket error %s errno=%d" % (err, err.errno)
    except socket.timeout:
        dbg.log(debug_fh, 'ERR', "API: socket timeout")
        return "API: socket timeout"
    except Exception as err:
       dbg.log(debug_fh, 'ERR', "API: other socket error %s" % err)
       return "API: other socket error %s" % err


def restart_server():
    # Delete the existing FIFO file used for communicating to the server
    if os.path.exists(req_fifo):
        os_command = "rm %s" % req_fifo
        os.system(os_command)

    # Start the server
    ha_server.start_server()


def main(argv):
    argc = len(argv)

    if argc != 3:
        show_api_usage()
        print "Invalid number of arguments %d" % argc
        return 1

    if argv[1] != "-c":
        show_api_usage()
        print "Invalid option %s" % argv[1]
        return 2

    if argv[2] == 'start':
        ha_server.start_server()
        return 0
    elif argv[2] == 'stop':
        cmd_string = 'stop'
    elif argv[2] == 'ping':
        cmd_string = 'ping'
    else:
        show_api_usage()
        print "Invalid command %s" % argv[2]
        return 3

    req_msg = send_command_to_server(cmd_string)
    if req_msg == 'OK':
        rsp_msg = get_response_from_server()
        if rsp_msg == 'OK':
            return 0
        else:
            return 4
    else:
        print req_msg

if __name__ == '__main__':
    sys.exit(main(sys.argv))
  


