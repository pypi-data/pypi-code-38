#!/usr/bin/env python3

import os
import sys
import logging
import argparse
import configparser

from RotL.windows import *

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)

REMEDIATION_TYPES = ['files', 'process_names', 'scheduled_tasks', 'services', 'directories', 'pids', 'registry_keys', 'registry_values']

def windows_remediate(remediation_script, output_file_path=None):
    """Create a windows remediation bat file from a remediation script.

    :param str remediation_script: The path to the remediation config file.
    """
    if not os.path.exists(remediation_script):
        logger.error("'{}' Does not exist".format(remediation_script))
        return False
    logger.info("Loaded remediation file'{}'".format(remediation_script))

    config = configparser.ConfigParser()
    config.read(remediation_script)

    commands = {'files': [],
                'process_names': [],
                'scheduled_tasks': [],
                'directories': [],
                'pids': [],
                'registry_keys': [],
                'registry_values': [],
                'services': []}

    if output_file_path is None:
        output_file_path = 'remediation.bat'

    # Order matters
    with open(output_file_path, 'w') as fp:
        processes = config['process_names']
        for p in processes:
            fp.write(kill_process_name(processes[p]))
            fp.write('\n')

        pids = config['pids']
        for p in pids:
            fp.write(kill_process_id(pids[p]))
            fp.write('\n')

        regValues = config['registry_values']
        for key in regValues:
            fp.write(delete_registry_value(regValues[key]))
            fp.write('\n')

        regKeys = config['registry_keys']
        for key in regKeys:
            fp.write(delete_registry_key(regKeys[key]))
            fp.write('\n')

        files = config['files']
        for f in files:
            fp.write(delete_file(files[f]))
            fp.write('\n')

        dirs = config['directories']
        for d in dirs:
            fp.write(delete_directory(dirs[d]))
            fp.write('\n')

        tasks = config['scheduled_tasks']
        for t in tasks:
            fp.write(delete_scheduled_task(tasks[t]))
            fp.write('\n')

        services = config['services']
        for s in services:
            fp.write(delete_service(services[s]))
            fp.write('\n')

    if os.path.isfile(output_file_path):
        logger.info("Wrote '{}'".format(output_file_path))
    return output_file_path


def write_template(rem_type):
    if rem_type == 'win':
        import shutil
        shutil.copyfile(os.path.join(BASE_DIR, 'templates', 'windows_remediation_template.ini'), 'remediate.ini')
        logger.info("Wrote 'remediate.ini'")
        return 'remediate.ini'
    else:
        return False

def main():

    choices=['win']#, 'mac']
    parser = argparse.ArgumentParser(description='Remediation off the Land: Write remediation files to execute')
    parser.add_argument('-w', '--write-template', choices=choices, help='write a remediation template file to local dir.')
    parser.add_argument('-f', '--remediation', action='store', help='the remediation file describing the infection')
    parser.add_argument('-t', '--os-type', help='remediation type (operating system)', choices=choices, default='win')
    parser.add_argument('-o', '--outfile', action='store', help='name of output file to write.', default=None)
    args = parser.parse_args()

    if args.write_template:
        result = write_template(args.write_template)
        if result:
           print('+ Wrote {}'.format(result))
        sys.exit()

    if args.remediation:
        if args.os_type == 'win':
            output = windows_remediate(args.remediation, output_file_path=args.outfile)
            if output:
                print("+ Wrote '{}'".format(output))
        else:
            print("Only windows remediation supported right now.")

    sys.exit()
