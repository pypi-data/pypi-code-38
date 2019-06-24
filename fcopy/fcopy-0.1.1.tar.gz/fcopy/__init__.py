import argparse
import optparse
import logging
from . import fcopy

def main():
    parser = argparse.ArgumentParser(description='A file copying utility.')

    group = parser.add_argument_group('selection options')
    group.add_argument("-c", "--conf", action='store', type=str, required=False, help="Loads a JSON configuration")
    group.add_argument("-t", "--task", action='append', type=str, required=False, help="Update the specified tasks")
    group.add_argument("-g", "--group", action='append', type=str, required=False, help="Update all task within the given groups")
    group.add_argument("-w", "--watch", action='store_true', required=False, help="Keeps watching for the files to be automatically updated")
    
    parser.add_argument("--version", action='version', version="copier " + fcopy.__version_str__)

    args = parser.parse_args()

    if (args.group):
        fcopy.update(args.group, args.watch)
    elif (args.task):
        fcopy.update(args.task, args.watch, 'name')
    elif (args.conf):
        fcopy.updateConfigPath(args.conf)
    else:
        parser.print_help()
