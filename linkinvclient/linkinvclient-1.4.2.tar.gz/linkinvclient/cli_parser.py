#!./venv/bin/python

# -*- coding: utf-8 -*-

import os
import sys
import argparse


possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
                                                

# 
# if os.path.exists(os.path.join(possible_topdir,
#                                'app1',
#                                '__init__.py')):
apppath = (os.path.join(possible_topdir,
                               'linkInventory',
                               'linkInventory'))
#    sys.path.insert(0, apppath)

sys.path.insert(0, apppath)

#print(sys.path)

from tokenleaderclient.configs.config_handler import Configs    
from  tokenleaderclient.client.client import Client 
from linkinvclient.client   import LIClient

auth_config = Configs()
tlclient = Client(auth_config)
c = LIClient(tlclient)

parser = argparse.ArgumentParser(add_help=False)


subparser = parser.add_subparsers()

li_parser = subparser.add_parser('list', help="call the ep3 api route from microservice micros1")

li_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "type all for listing all links or serial number for a songle link to list"
                  )

try:                    
    options = parser.parse_args()  
except:
    #print usage help when no argument is provided
    parser.print_help(sys.stderr)    
    sys.exit(1)

def main():
    if len(sys.argv)==1:
        # display help message when no args are passed.
        parser.print_help()
        sys.exit(1)   
   
    #print(sys.argv)
    
    if  sys.argv[1] == 'list':
        if options.name == 'all':            
            print(c.list_links())
        else:
            print(c.list_link_by_slno(options.name))    
                    
     
    
if __name__ == '__main__':
    main()
    
'''
/mnt/c/mydev/microservice-tsp-billing/tokenleader$ ./tokenadmin.sh  -h    to get help
'''
    
    
