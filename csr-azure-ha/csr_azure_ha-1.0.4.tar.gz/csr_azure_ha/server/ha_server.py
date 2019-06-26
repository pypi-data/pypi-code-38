#!/usr/bin/env python

import os
import sys
import stat
import time
import socket
from multiprocessing import Process, Pipe
from node_mgr import NodeTable
import event_mgr
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell')
import azure_dbg as dbg

server_running = False
sock_file = "/home/guestshell/azure/HA/sock_file"
debug_file = "/home/guestshell/azure/HA/azha.log"


def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def create_node(table, params, debug_fh):
    dbg.log(debug_fh, 'INFO', "Server processing create_node command")
    return table.create_node(params, debug_fh)

def set_params(table, params, debug_fh):
    dbg.log(debug_fh, 'INFO', "Server processing set_params command")
    return table.set_params(params, debug_fh)

def clear_params(table, params, debug_fh):
    dbg.log(debug_fh, 'INFO', "Server processing clear_params command")
    return table.clear_params(params, debug_fh)

def show_node(table, params, debug_fh):
    if params['index'] == '0':
        table.show_table()
        dbg.log(debug_fh, 'INFO', "See output on server")
        return "OK"
    else:
        node_desc = table.show_node(params, debug_fh)
        return node_desc
    
def delete_node(table, params, debug_fh):
    dbg.log(debug_fh, 'INFO', "Server processing delete_node command")
    return table.delete_node(params, debug_fh)

def event_on_one_node(event_type, node, params, debug_fh):
    index = node['index']
    if event_type == 'revert':
        if 'mode' in node:
            if node['mode'] == 'primary':
                event_mgr.handle_event(node, event_type)
    else:
        dbg.log(debug_fh, 'INFO', "Server processing %s node_event" % event_type)
        event_mgr.handle_event(node, event_type)    

def node_event(table, params, debug_fh):
    index = int(params['index'])
    event_type = params['event']
    if index == 0:
        # Index of zero. Process this event for all nodes.
        for node in table.nodes:
            event_on_one_node(event_type, node, params, debug_fh)
    else:
        node = table.find_node(params['index'], debug_fh)
        if node == None:
            dbg.log(debug_fh, 'ERR', "Node %d not found for event %s" % (index, event_type))
            return "Node %d not found for event %s" % (index, event_type)
        else:
            event_on_one_node(event_type, node, params, debug_fh)
            
    return "OK"


def build_command_dict(cmd_list):
    cmd_dict = {}
    i = 1
    while i < len(cmd_list):
        if cmd_list[i] == '-i':
            keyword = "index"
        elif cmd_list[i] == '-p':
            keyword = "cloud"
        elif cmd_list[i] == '-s':
            keyword = "subscriptionId"
        elif cmd_list[i] == '-g':
            keyword = "resourceGroup"
        elif cmd_list[i] == '-t':
            keyword = "routeTableName"
        elif cmd_list[i] == '-r':
            keyword = "route"
        elif cmd_list[i] == '-n':
            keyword = "nextHop"
        elif cmd_list[i] == '-m':
            keyword = "mode"
        elif cmd_list[i] == '-a':
            keyword = "appId"
        elif cmd_list[i] == '-d':
            keyword = "tenantId"
        elif cmd_list[i] == '-k':
            keyword = "appKey"
        elif cmd_list[i] == '-c':
            keyword = "command"
        elif cmd_list[i] == '-e':
            keyword = "event"
        elif cmd_list[i] == '':
            break
        else:
            dbg.log(debug_fh, 'ERR', "Invalid command format %s" % cmd_list[i])
            print "Invalid command format %s" % cmd_list[i]
        value = cmd_list[i+1]
        i = i + 2
        cmd_dict[keyword] = value
#        print "Added keyword %s with value %s" % (keyword, value)
    return cmd_dict

                
def server():
    global debug_fh

    # Find out the process ID
    pid = os.getpid()

    # Open up a file to write error and debug messages
    debug_fh = open(debug_file, "a", os.O_NONBLOCK)
    dbg.log(debug_fh, 'INFO', "High availability server started with pid=%d" % pid)
    
    # Create an instance of the node manager
    nodeTable = NodeTable(debug_fh)

    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Bind the socket to the port
    sock.bind(sock_file)

    # Listen for incoming connections
    sock.listen(1)

    while server_running:
        try:
            # Wait for a connection
            connection, client_address = sock.accept()

            # Read a command from the client
            line = connection.recv(300)
            cmd_list = line.rsplit(' ')
            cmd_name = cmd_list[0]

            ret_msg = ''
            # Call the function that handles this command
            if cmd_name != 'clear_params' :
                cmd_dict = build_command_dict(cmd_list)
                
            if cmd_name == 'create_node' :
                ret_msg = create_node(nodeTable, cmd_dict, debug_fh)
            elif cmd_name == 'set_params' :
                ret_msg = set_params(nodeTable, cmd_dict, debug_fh)
            elif cmd_name == 'clear_params' :
                ret_msg = clear_params(nodeTable, cmd_list, debug_fh)
            elif cmd_name == 'show_node' :
                ret_msg = show_node(nodeTable, cmd_dict, debug_fh)
            elif cmd_name == 'delete_node' :
                ret_msg = delete_node(nodeTable, cmd_dict, debug_fh)
            elif cmd_name == 'node_event' :
                ret_msg = node_event(nodeTable, cmd_dict, debug_fh)
            elif cmd_name == 'stop' :
                ret_msg = stop_server()
            elif cmd_name == 'ping' :
                ret_msg = 'OK'
            else:
                ret_msg = "Unknown server command %s" % cmd_name
                dbg.log(debug_fh, 'ERR', "Unknown server command %s" % cmd_name)
                
            connection.sendall(ret_msg)

        except socket.error as err:
            dbg.log(debug_fh, 'ERR', "Server socket error %d" % err.errno)
        except Exception as e:
            dbg.log(debug_fh, 'ERR', "HA server caught exception %s" % e)
            tb = traceback.format_exc()
            dbg.log(debug_fh, 'ERR', "%s" % tb)
            connection.sendall(e.message)

    # Clean up the connection
    dbg.log(debug_fh, 'INFO', "Server exiting")
    debug_fh.close()
    connection.close()
    return 0


def send_cmd(cmd):
    fifo_to_server = os.open(fifo, os.O_WRONLY)
    os.write(fifo_to_server, cmd)
    os.close(fifo_to_server)


def start_server():
    global server_running

    print "Starting the high availability server"
    server_running = True

    # Make sure the socket does not already exist
    try:
        os.unlink(sock_file)
    except OSError:
        if os.path.exists(sock_file):
            os_command = "rm %s" % sock_file
            os.system(os_command)

    p = Process(target=server, args=())
    p.start()
    p.join()

    
def stop_server():
    global server_running
    
    print "Processing a stop_server command"
    server_running = False
    os_command = "rm %s" % req_fifo
    os.system(os_command)
    return 'OK'



def main(argv):

    argc = len(argv)
    if argv[1] == "start":
        start_server()

    elif argv[1] == "stop":
        stop_server()
        return 0

    else:
        print "Usage: ha_server.py {start | stop}"
        return 'ERR1'

if __name__ == '__main__':
    sys.exit(main(sys.argv))
