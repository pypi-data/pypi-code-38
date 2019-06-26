#!/usr/bin/env python

import os
import sys
import ast

sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell')
import azure_dbg as dbg
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell/MetadataMgr')
from metadata import MetaData

node_file = '/home/guestshell/azure/HA/node_file'

class NodeTable:

    md = None

    def __doc__(self):
        "This class represents a list of redundancy nodes"

    def __init__(self, debug_fh):
        self.nodes = []
        NodeTable.md = MetaData()
        self.read_table_from_file(debug_fh)


    def create_node(self, params, debug_fh):
        # Check if the node already exists
        node_index = params['index']
        node = self.find_node(node_index, debug_fh)
        if node != None:
            # Node already exists. Just update its parameters
            return self.set_params(params, debug_fh)

        node = params
        try:
            subscrId = node['subscriptionId']
        except KeyError:
            if os.path.exists("'/home/guestshell/azure/tools/MetadataMgr/metadata.json"):
                subscrId = NodeTable.md.get_subscriptionId()
                if subscrId != '':
                    node['subscriptionId'] = subscrId

        try:
            resGrp = node['resourceGroup']
        except KeyError:
            if os.path.exists("'/home/guestshell/azure/tools/MetadataMgr/metadata.json"):
                resGrp = NodeTable.md.get_resourceGroup()
                if resGrp != '':
                    node['resourceGroup'] = resGrp

        try:
            nextHop = node['nextHop']
        except KeyError:
            if os.path.exists("'/home/guestshell/azure/tools/MetadataMgr/metadata.json"):
                nextHop = NodeTable.md.get_private_ipaddr()
                if nextHop != '':
                    node['nextHop'] = nextHop

        self.nodes.append(node)
        self.write_table_to_file()
        dbg.log(debug_fh, 'INFO', "Created new node with index %s" % node['index'])
        return "OK"


    def set_params(self, new_params, debug_fh):
        node_index = new_params['index']
        node = self.find_node(node_index, debug_fh)
        if node == None:
            dbg.log(debug_fh, 'INFO', "Node with index %s not found" % node_index)
            return self.create_node(new_params, debug_fh)
    
        for param in new_params.keys():
            node[param] = new_params[param]
        self.write_table_to_file()
        dbg.log(debug_fh, 'INFO', "Set parameters on node with index %s" % node_index)
        return "OK"

    
    def clear_params(self, old_params, debug_fh):
        node_index = ''
        i = 0
        for token in old_params:
            if token == '-i':
                node_index = old_params[i+1]
                break
            i = i + 1
        if node_index == '':
            dbg.log(debug_fh, 'ERR', "Node index not found in command")
            return "ERR1"
        
        node = self.find_node(node_index, debug_fh)
        if node == None:
            dbg.log(debug_fh, 'ERR', "Node with index %s not found" % node_index)
            return "ERR1"
        i = 1
        while i < len(old_params):
            if old_params[i] == '-i':
                index = old_params[i+1]
                # Can not clear the index parameter
                keyword = "dummy"
                i = i + 1
            elif old_params[i] == '-s':
                keyword = "subscriptionId"
            elif old_params[i] == '-g':
                keyword = "resourceGroup"
            elif old_params[i] == '-t':
                keyword = "routeTableName"
            elif old_params[i] == '-r':
                keyword = "route"
            elif old_params[i] == '-n':
                keyword = "nextHop"
            elif old_params[i] == '-m':
                keyword = "mode"
            elif old_params[i] == '-a':
                keyword = "appId"
            elif old_params[i] == '-d':
                keyword = "tenantId"
            elif old_params[i] == '-k':
                keyword = "appKey"
            else:
                print "Invalid parameter format %s" % old_params[i]

            if keyword in node:
                del node[keyword]
            i = i + 1
            
        self.write_table_to_file()
        dbg.log(debug_fh, 'INFO', "Cleared parameters on node with index %s" % node_index)
        return "OK"

    
    def delete_node(self, param, debug_fh):
        node_index = param['index']
        node = self.find_node(node_index, debug_fh)
        if node == None:
            dbg.log(debug_fh, 'ERR', "Node with index %s not found" % node_index)
            return "ERR1"
    
        self.nodes.remove(node)
        self.write_table_to_file()
        dbg.log(debug_fh, 'INFO', "Deleted node with index %s" % node_index)
        return "OK"


    def find_node(self, index, debug_fh):
        for node in self.nodes:
            # Find the existing node
            if node['index'] == index:
                return node
        return None


    def show_node(self, param, debug_fh):
        # Parameter should only be the node index
        node_index = param['index']
        node = self.find_node(node_index, debug_fh)
        if node == None:
            return "Node with index %s not found" % node_index
        node_str = "Redundancy node configuration:\n"
        for key in node:
            param_str = "%s \t%s \n" % (key, node[key])
            node_str = node_str + param_str
        return node_str


    def show_table(self):
        for node in self.nodes:
            print "Redundancy node %s:" % node['index']
            for param in node:
                print "\t%s \t%s" % (param, node[param])


    def write_table_to_file(self):
        with open(node_file, 'w') as write_fh:
            for node in self.nodes:
                out_str = str(node) + '\n'
                write_fh.write(out_str)


    def read_table_from_file(self, debug_fh):
        if os.path.exists(node_file):
            with open(node_file, 'r') as read_fh:
                for line in read_fh:
                    input_str = line.strip()
                    node = ast.literal_eval(input_str)
                    self.create_node(node, debug_fh)

