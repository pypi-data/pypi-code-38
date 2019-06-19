#!/usr/bin/env python3

import os
import sys
import time
import argparse
import logging
import coloredlogs
import pprint
from lerc_control import lerc_api, collect
from lerc_control.scripted import execute_script
from lerc_control.helpers import TablePrinter

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# configure logging #
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
# set noise level
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('lerc_api').setLevel(logging.INFO)
logging.getLogger('lerc_control').setLevel(logging.INFO)
#logging.getLogger('lerc_control.scripted').setLevel(logging.INFO)
#logging.getLogger('lerc_control.collect').setLevel(logging.INFO)

logger = logging.getLogger('lerc_ui')
coloredlogs.install(level='INFO', logger=logger)

try:
    from lerc_control import deploy_lerc
except:
    pass

def main():

    parser = argparse.ArgumentParser(description="User interface to the LERC control server")
    # LERC environment choices
    config = lerc_api.load_config()
    env_choices = [ sec for sec in config.sections() if config.has_option(sec, 'server') ]
    parser.add_argument('-e', '--environment', action="store", default='default', 
                        help="specify an environment to work with. Default='default'", choices=env_choices)
    parser.add_argument('-d', '--debug', action="store_true", help="set logging to DEBUG", default=False)
    parser.add_argument('-c', '--check', action="store", help="check on a specific command id")
    parser.add_argument('-r', '--resume', action='store', help="resume a pending command id") 
    parser.add_argument('-g', '--get', action='store', help="get results for a command id")

    subparsers = parser.add_subparsers(dest='instruction') #title='subcommands', help='additional help')

    # Query
    parser_query = subparsers.add_parser('query', help="Query the LERC Server")
    parser_query.add_argument('query', help="The search you want to run. Enter 'fields' to see query fields.")
    parser_query.add_argument('-rc', '--return-commands', action='store_true', help="Return command results (even if no cmd fields specified)")
 
    # Initiate new LERC commands
    parser_run = subparsers.add_parser('run', help="Run a shell command on the host.")
    parser_run.add_argument('hostname', help="the host you'd like to work with")
    parser_run.add_argument('command', help='The shell command for the host to execute`')
    parser_run.add_argument('-a', '--async', action='store_true', help='Set asynchronous to true (do NOT wait for output or command to complete)')
    parser_run.add_argument('-p', '--print-only', action='store_true', help='Only print results to screen.')
    parser_run.add_argument('-w', '--write-only', action='store_true', help='Only write results to file.')
    parser_run.add_argument('-o', '--output-filename', default=None, action='store', help='Specify the name of the file to write any results to.')

    parser_upload = subparsers.add_parser('upload', help="Upload a file from the client to the server")
    parser_upload.add_argument('hostname', help="the host you'd like to work with")
    parser_upload.add_argument('file_path', help='the file path on the client')

    parser_download = subparsers.add_parser('download', help="Download a file from the server to the client")
    parser_download.add_argument('hostname', help="the host you'd like to work with")
    parser_download.add_argument('file_path', help='the path to the file on the server')
    parser_download.add_argument('-f', '--local-file', help='where the client should write the file')

    parser_quit = subparsers.add_parser('quit', help="tell the client to uninstall itself")
    parser_quit.add_argument('hostname', help="the host you'd like to work with")

    # response functions
    parser_collect = subparsers.add_parser('collect', help="Default (no arguments): perform a full lr.exe collection")
    parser_collect.add_argument('-d', '--directory', action='store', help="Compress contents of a client directory and collect")
    parser_collect.add_argument('-mc', '--multi-collect', action='store', help="Path to a multiple collection file")
    parser_collect.add_argument('hostname', help="the host you'd like to work with")

    parser_contain = subparsers.add_parser('contain', help="Contain an infected host")
    parser_contain.add_argument('hostname', help="the host you'd like to work with")
    parser_contain.add_argument('-on', action='store_true', help="turn on containment")
    parser_contain.add_argument('-off', action='store_true', help="turn off containment")
    parser_contain.add_argument('-s', '--status', action='store_true', help="Get containment status of host")

    parser_script = subparsers.add_parser('script', help="run a scripted routine on this lerc.")
    parser_script.add_argument('hostname', help="the host you'd like to work with")
    parser_script.add_argument('-l', '--list-scripts', action='store_true', help="list scripts availble to lerc_ui")
    parser_script.add_argument('-s', '--script-name', help="provide the name of a script to run")
    parser_script.add_argument('-f', '--file-path', help="the path to a custom script you want to execute")

    parser_remediate = subparsers.add_parser('remediate', help="Remediate an infected host")
    parser_remediate.add_argument('hostname', help="the host you'd like to work with")
    parser_remediate.add_argument('--write-template', action='store_true', default=False, help='write the remediation template file as remediate.ini')
    parser_remediate.add_argument('-f', '--remediation-file', help='the remediation file describing the infection')
    parser_remediate.add_argument('-drv', '--delete-registry-value', help='delete a registry value and all its data')
    parser_remediate.add_argument('-drk', '--delete-registry-key', help='delete all values at a registry key path')
    parser_remediate.add_argument('-df', '--delete-file', help='delete a file')
    parser_remediate.add_argument('-kpn', '--kill-process-name', help='kill all processes by this name')
    parser_remediate.add_argument('-kpid', '--kill-process-id', help='kill process id')
    parser_remediate.add_argument('-dd', '--delete-directory', help='Delete entire directory')
    parser_remediate.add_argument('-ds', '--delete-service', help='Delete a service from the registry and the ServicePath from the file system.')
    parser_remediate.add_argument('-dst', '--delete-scheduled-task', help='Delete a scheduled task by name')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger('lerc_api').setLevel(logging.DEBUG)
        logging.getLogger('lerc_control').setLevel(logging.DEBUG)
        coloredlogs.install(level='DEBUG', logger=logger)

    # a local lerc_session will be needed to go any further
    ls = lerc_api.lerc_session(profile=args.environment)

    if args.instruction == 'query':
        if args.query == 'fields':
            print("\nAvailable query fields:\n")
            fmt = [ ('Field', 'field', 14),
                    ('Description', 'description', 80) ]
            print( TablePrinter(fmt, sep='  ', ul='=')(lerc_api.QUERY_FIELD_DESCRIPTIONS) )
            print()
            print("NOTE:")
            print("  1) Fields are ANDed by default. Fields can be negated by appending '-' or '!' to the front of the field (no space) or by specifying 'NOT ' in front of the field (space).")
            print("  2) A leading '-' with no space in front will cause the argument parser to misinterpret the query as a command line argument option.")
            print() 
            sys.exit()
        query = lerc_api.parse_lerc_server_query(args.query)
        if args.return_commands: 
            query['rc'] = True
        results = ls.query(**query)
        clients = [ c.get_dict for c in results['clients']]
        fmt = [ ('ID', 'id', 5),
                ('Hostname', 'hostname', 20),
                ('Status', 'status', 11),
                ('Version', 'version', 8),
                ('Sleep Cycle', 'sleep_cycle', 11),
                ('Install Date', 'install_date', 20),
                ('Last Activity', 'last_activity', 20),
                ('Company ID', 'company_id', 10)]
        print("\nClient Results:\n")
        print( TablePrinter(fmt, sep='  ', ul='=')(clients))
        print("Total Client Results:{}".format(len(clients)))
        print()
        commands = [ c.get_dict for c in results['commands']]
        if commands:
            fmt = [ ('ID', 'command_id', 9),
                    ('Client ID', 'client_id', 9),
                    ('Hostname', 'hostname', 20),
                    ('Operation', 'operation', 11),
                    ('Status', 'status', 9)]
                  #  ('Version', 'version', 8),
                  #  ('Sleep Cycle', 'sleep_cycle', 11),
                  #  ('Install Date', 'install_date', 20),
                  #  ('Last Activity', 'last_activity', 20)]
            print("\nCommand Results:\n")
            print( TablePrinter(fmt, sep='  ', ul='=')(commands))
            #for cmd in commands:
            #    print(cmd)
            print() 
        sys.exit()

    # root options
    if args.check:
        command = ls.get_command(args.check)
        print(command)
        if command.status == 'ERROR':
            print("ERROR Report:")
            pprint.pprint(command.get_error_report(), indent=5)
        sys.exit()
    elif args.get:
        command = ls.get_command(args.get)
        if command:
            command.get_results(chunk_size=16384)
            print(command)
        sys.exit()
    elif args.resume:
        command = ls.get_command(args.resume)
        command.wait_for_completion()
        if command:
            print(command)
        sys.exit()

    # if we're here, then an instructions been specified and the args.hostname is a thing
    client = ls.get_host(args.hostname)
    if isinstance(client, list):
        logger.critical("More than one result. Not handled yet..")
        for c in client:
            print(c)
            print()
        sys.exit(1) 

    # Auto-Deployment Jazz
    bad_status = False
    if client:
        if client.status == 'UNINSTALLED' or client.status == 'UNKNOWN':
            logger.info("Non-working client status : {}".format(client.status))
            bad_status = True

    if not client or bad_status:
        config = ls.get_config
        if config.has_option('default', 'cb_auto_deploy') and not config['default'].getboolean('cb_auto_deploy'):
            logger.info("CarbonBlack auto-deployment turned off. Exiting..")
            sys.exit(0)
        logger.info("Attempting to deploy lerc with CarbonBlack..")
        try:
            from cbapi import auth
            from deploy_lerc import deploy_lerc, CbSensor_search
        except:
            logger.error("Failed to import deployment functions from lerc_control.deploy_lerc OR cbapi.")
            sys.exit(1)
        logging.getLogger('lerc_control.deploy_lerc').setLevel(logging.ERROR)
        environments = auth.FileCredentialStore("response").get_profiles()
        sensors = []
        logger.debug("Trying to find the sensor in the available carbonblack environments.")
        for env in environments:         
            sensor = CbSensor_search(env, args.hostname)
            if sensor:
                logger.debug("Found sensor in {} environment".format(env))
                sensors.append((env, sensor))
        if len(sensors) > 1:
            logger.error("A CarbonBlack Sensor was found by that hostname in multiple environments.")
            sys.exit(1)
        elif sensors:
            logging.getLogger('lerc_control.deploy_lerc').setLevel(logging.INFO)
            sensor = sensors[0][1]
            config = lerc_api.check_config(config, required_keys=['lerc_install_cmd', 'client_installer'])
            result = deploy_lerc(sensor, config[sensors[0][0]]['lerc_install_cmd'], lerc_installer_path=config['default']['client_installer'])
            if result: # modify deploy_lerc to use new client objects
                logger.info("Successfully deployed lerc to this host: {}".format(args.hostname))
                client = ls.get_host(args.hostname)
        else:
            logger.error("Didn't find a sensor in CarbonBlack by this hostname")
            sys.exit(0)
 
    # remediation
    if args.instruction == 'remediate':
        if not args.debug:
            logging.getLogger('lerc_control.lerc_api').setLevel(logging.WARNING)

        if args.write_template:
           import shutil
           shutil.copyfile(os.path.join(BASE_DIR, 'etc', 'example_remediate_routine.ini'), 'remediate.ini')
           print("Wrote remediate.ini")
           sys.exit(0)
        from lerc_control import remediate
        if args.remediation_file:
            remediate.Remediate(client, args.remediation_file)
        if args.kill_process_name:
            cmd = remediate.kill_process_name(client, args.kill_process_name)
            remediate.evaluate_remediation_results(cmd, 'process_names', args.kill_process_name)
        if args.kill_process_id:
            cmd = remediate.kill_process_id(client, args.kill_process_id)
            remediate.evaluate_remediation_results(cmd, 'pids', args.kill_process_id)
        if args.delete_registry_value:
            cmd = remediate.delete_registry_value(client, args.delete_registry_value)
            remediate.evaluate_remediation_results(cmd, 'registry_values', args.delete_registry_value)
        if args.delete_registry_key:
            cmd = remediate.delete_registry_key(client, args.delete_registry_key)
            remediate.evaluate_remediation_results(cmd, 'registry_keys', args.delete_registry_key)
        if args.delete_file:
            cmd = remediate.delete_file(client, args.delete_file)
            remediate.evaluate_remediation_results(cmd, 'files', args.delete_file)
        if args.delete_directory:
            cmd = remediate.delete_directory(client, args.delete_directory)
            remediate.evaluate_remediation_results(cmd, 'directories', args.delete_directory)
        if args.delete_scheduled_task:
            cmd = remediate.delete_scheduled_task(client, args.delete_scheduled_task)
            remediate.evaluate_remediation_results(cmd, 'scheduled_tasks', args.delete_scheduled_task)
        if args.delete_service:
            # delete_service returns a list of commands it issued
            cmds = remediate.delete_service(client, args.delete_service, auto_fill=True)
            for cmd in cmds:
                if isinstance(cmd, tuple):
                    remediate.evaluate_remediation_results(cmd[0], cmd[1], cmd[2])
                else:
                    remediate.evaluate_remediation_results(cmd, 'services', args.delete_service)
        sys.exit(0)

    # collections
    profile=args.environment if args.environment else 'default'
    if args.instruction == 'collect':
        if not args.debug:
            logging.getLogger('lerc_control.lerc_api').setLevel(logging.WARNING)
        if args.directory:
            commands = collect.get_directory(client, args.directory)
        elif args.multi_collect:
            collect.multi_collect(client, args.multi_collect)
        else:
            collect.full_collection(client)
        sys.exit(0)

    if args.instruction == 'script':
        config = ls.get_config
        if args.list_scripts:
            if not config.has_section('scripts'):
                print("\nNo pre-existing scripts have been made availble.")
                sys.exit(0)           
            print("\nAvailable scripts:")
            for sname in config['scripts']:
                print("\t{}".format(sname))
            print()
            sys.exit(0)
        elif args.script_name:
            if not config.has_option('scripts', args.script_name):
                logger.error("{} is not a defined script".format(args.script_name))
                sys.exit(1)
            script_path = config['scripts'][args.script_name]
            commands = execute_script(client, script_path)
            sys.exit(0)
        elif args.file_path:
            if not os.path.exists(args.file_path):
                logger.error("Could not find script file at '{}'".format(args.file_path))
                sys.exit(1)
            commands = execute_script(client, args.file_path)
            sys.exit(0)
        else:
            logger.info("No argument was specified for the script command. Exiting.")
            sys.exit(0)

    # Else, see if we're running a command directly
    cmd = None
    if args.instruction == 'run':
        if args.async:
            cmd = client.Run(args.command, async=args.async)
        else:
            cmd = client.Run(args.command)

    elif args.instruction == 'contain':
        if args.on:
            client.contain()
        elif args.off:
            client.release_containment()
        elif args.status:
            print("Containment status check not yet implemented.")

    elif args.instruction == 'download':
        # if client_file_path is not specified the client will write the file to it's local dir
        analyst_file_path = os.path.abspath(args.file_path)
        file_name = args.file_path[args.file_path.rfind('/')+1:]
        if args.local_file is None:
            args.local_file = file_name
        cmd = client.Download(file_name, client_file_path=args.local_file, analyst_file_path=analyst_file_path)

    elif args.instruction == 'upload':
        cmd = client.Upload(args.file_path)

    elif args.instruction == 'quit':
        cmd = client.Quit()
    elif args.check:
        command = ls.get_command(args.check)
        print(command)
        sys.exit()
    elif args.get:
        command = ls.get_command(args.get)
        if command:
            command.get_results(chunk_size=16384)
            print(command)
        sys.exit()
    elif args.resume:
        command = ls.get_command(args.resume)
        command.wait_for_completion()
        if command:
            print(command)
        sys.exit()
    else:
        print(client)
        sys.exit()

    if not cmd:
        sys.exit(1)

    start_time = time.time() 
    if not cmd.wait_for_completion():
        logger.warning("{} (ID:{}) command went to a {} state. Exiting.".format(cmd.operation, cmd.id, cmd.status))
        sys.exit(1)
    logger.info("{} command {} completed successfully".format(cmd.operation, cmd.id))
    content = None
    if args.instruction == 'run':
        if args.print_only:
            content = cmd.get_results(return_content=args.print_only)
            print(content.decode('utf-8'))
        elif args.write_only:
            cmd.get_results(print_run=False, file_path=args.output_filename)
        else:
            cmd.get_results()
    else:
        cmd.get_results()

    print(cmd)

    sys.exit()

