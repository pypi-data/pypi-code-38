# coding: utf-8
# Copyright (c) JUMP2 Development Team.
# Distributed under the terms of the JLU License.


#=================================================================
# This file is part of JUMP2.
#
# Copyright (C) 2017 Jilin University
#
#  Jump2 is a platform for high throughput calculation. It aims to 
#  make simple to organize and run large numbers of tasks on the 
#  superclusters and post-process the calculated results.
#  
#  Jump2 is a useful packages integrated the interfaces for ab initio 
#  programs, such as, VASP, Guassian, QE, Abinit and 
#  comprehensive workflows for automatically calculating by using 
#  simple parameters. Lots of methods to organize the structures 
#  for high throughput calculation are provided, such as alloy,
#  heterostructures, etc.The large number of data are appended in
#  the MySQL databases for further analysis by using machine 
#  learning.
#
#  Jump2 is free software. You can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published 
#  by the Free sofware Foundation, either version 3 of the License,
#  or (at your option) and later version.
# 
#  You should have recieved a copy of the GNU General Pulbic Lincense
#  along with Jump2. If not, see <https://www.gnu.org/licenses/>.
#=================================================================

"""
This module defines the classes relating to basic parses.
"""


__author__ = "Xin-Gang Zhao"
from ..config.cluster import Cluster

def collect_parses():

    parse = get_parse()
    cluster = Cluster()

    (options, args) = parse.parse_args()
    all_option = {}
    
    if options.single is not None:
        all_option = {'single':{'path':options.single, \
                                'task':args[0]}}
        return all_option 
    #input examples % 
    if options.script_module is not None:
        script = options.script_module
        all_option={'script':script}
        print script 
    #parallel environments % 
    if options.cores is not None:
        cluster.cores = options.cores 
    if options.nodes is not None:
        cluster.nodes = options.nodes
    if options.queue is not None:
        cluster.queue = options.queue
    if options.max_jobs is not None:
        cluster.max_jobs = options.max_jobs

    all_option['cluster'] = cluster.scripts

    #run/output the required files for calc % 
    if options.submit_tasks is not None:
        run = options.submit_tasks 
        all_option['run'] = run
    #file to store data for calculation % 
    if options.pool_name is not None:
        pool_name = options.pool_name 
    #else:
    #    pool_name = 'test'
    
        all_option['pool'] = pool_name
    #overwrite/update the all the data % 
    all_option['overwrite'] = options.overwrite
    all_option['update'] = options.update_change

    #backup files % 
    all_option['tarfile'] = options.tar_files
    #extract data % 
    if options.extract_data is not None:
        extract = options.extract_data
        all_option['extract'] = args
    
    #store the data % 
    all_option['append'] = options.append2db

    #check the status %
    if options.check_status is not None:
        check = options.check_status
    else:
        check = False
    
    all_option['check'] = check
    all_option['args'] = args

    #remote log/submit %
    if options.ssh_log is not None:
	username = options.ssh_log.split('@')[0]
	ssh_ip = options.ssh_log.split('@')[1].split(':')[0]
	if ':' in options.ssh_log:
	    ssh_port = options.ssh_log.split(':')[-1]
	else:
	    ssh_port = 22
	all_option['ssh'] = {'user':username, 'ip':ssh_ip, 'port':ssh_port}  
    else:
	all_option['ssh'] = None

    return all_option

def get_parse():

    from optparse import OptionParser, OptionGroup

    parse = OptionParser('jump2 [options]  args')
    parse.set_defaults(\
                      script_module = None,
                            cores   = None,
                            single  = None,
                            nodes   = None, 
                            queue   = None,
                          max_jobs  = None,
                         overwrite  = None,
                       append2db    = None, 
                       pool_name    = None, 
                       submit_tasks = None,  
                       extract_data = None,  
                       check_status = None,   
                       tar_files    = None,   
                       ssh_log      = None,   
                      update_change = None)   

    #parses for default commands
    
    group_run = OptionGroup(parse, "Flags for preparing files for calculation:")
    group_extract = OptionGroup(parse, "Flags for extracting data from results:")
    group_check = OptionGroup(parse, "Flags for checking the status of tasks:")
    group_cluster = OptionGroup(parse, "Flags for managing:")

    group_run.add_option('-i', '--input', dest='script_module', action='store', 
                     metavar='FILE', default=None, choices=['vasp', 'win2k', 'abinit', 'pwscf', 'gaussian'], 
                     help='Present a basic example for calculation.\n')

    group_run.add_option('-f', '--file', dest='pool_name', action='store', 
                     type='string', default=None, help='Pool name for storing the calculating data.\n')

    group_run.add_option('--single', dest='single', action='store', 
                     type='string', default=None, help='one task information for single projection.\n')

    group_run.add_option('-r', '--run', dest='submit_tasks', type='choice',
                     default=None, choices=['input', 'qsub', 'prepare'],
                     help='Submit the tasks according to the input data.\n')

    group_extract.add_option('-s', '--save', dest='append2db', action='store_true', 
                     default=False, help='Store the extract data in to database.\n')
    
    group_run.add_option('--overwrite', dest='overwrite', action='store_true', 
                     default=False, help='Whether to overwrite files.\n')
    
    group_cluster.add_option('--cores', dest='cores', action='store', 
                     type='int', default=None, help='How many codes to be used for one task.\n')

    group_cluster.add_option('--queue', dest='queue', action='store', 
                     type='string', default=None, help='Which queue for projecting tasks.\n')

    group_cluster.add_option('--num', dest='max_jobs', action='store', 
                     type='int', default=10, help='The maxmium number of jobs to be submit at once.\n')

    group_cluster.add_option('--nodes', dest='nodes', action='store', 
                     type='int', default=None, help='How many cluster to be used.\n')

    group_extract.add_option('-e', '--extract', dest='extract', action='store_true', default=False,
                     help='Extracting data from the calculated results.\n')
                     #choices=['total_energy', 'structure', 'gap', 'band', 'dos', 'optics'], 
    
    group_check.add_option('-c', '--check', dest='check_status', action='store', 
                     default='all', choices=['all', 'done', 'error', 'running', 'wait'],
                     help='Check status of tasks.\n')
    
    group_extract.add_option('-t', '--tar', dest='tar_files', action='store_true', 
                     default=False, help='backup the data to a tarfile named xx.tar.bz2\n')
    
    group_run.add_option('-u', '--update', dest='update_change', action='store_true', 
                     default=False, help='Update the changes/modification.\n')
   
    group_cluster.add_option('--ssh', dest='ssh_log', action='store', type='string', 
                     default=None, help='remote manager the tasks, using --ssh=username@192.168.1.1:port\n')

    parse.add_option_group(group_run)
    parse.add_option_group(group_cluster)
    parse.add_option_group(group_extract)
    parse.add_option_group(group_check)
    return parse

