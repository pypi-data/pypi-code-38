#!/usr/bin/env python

# Import OS package
import os
import sys
from csr_azure_ha.server import convert_str as cs

node_file = '/home/guestshell/azure/HA/node_file'


node1 = {'cidr_ip':'15.0.0.0/8',
         'def_gw_ip':'12.0.99.15',
         'route_table':'msi-sub2-RouteTable',
         'res_group':'msi-rg',
         'subscriptId':'b0b1a9e2' }

def showNode(node):
    print "CIDR IP address = %s" % node['cidr_ip']
    print "Gateway IP address = %s" % node['def_gw_ip']
    print "Route table = %s" % node['route_table']
    print "Resource group = %s" % node['res_group']
    print "Subscription ID = %s" % node['subscriptId']

def writeNodeToFile(node, fh):
    out_str = str(node) + '\n'
    fh.write(out_str)

def readNodeFromFile(fh):
    line = fh.read()
    input_str = line.strip()
    var_type = cs.determine_type_from_str(input_str)
    node = cs.convert_str_to_variable(input_str, var_type)
    return node

def main(node):
    showNode(node)
    write_fh = open(node_file, 'w')
    writeNodeToFile(node, write_fh)
    write_fh.close()

    read_fh = open(node_file, 'r')
    readNode = readNodeFromFile(read_fh)
    print "main: end keys are %s" % readNode.keys()
#    print "main: CIDR = %s" % readNode["'cidr_ip'"]
#    showNode(readNode)
    read_fh.close()


if __name__ == '__main__':
    sys.exit(main(node1))
