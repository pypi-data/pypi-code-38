#!/usr/bin/env python

"""list s3 bucket objects in a tree-like format."""

import argparse
from argparse import RawTextHelpFormatter as rawtxt
import sys
import signal
import os
from os.path import expanduser
import shutil
import json
import subprocess
from datetime import datetime
from pathlib import Path

def signal_handler(sig, frame):
    """handle control c"""
    print('\nuser cancelled')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def query_yes_no(question, default="yes"):
    '''confirm or decline'''
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("\nPlease respond with 'yes' or 'no' (or 'y' or 'n').\n")

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None

class Bcolors:
    """console colors"""
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    GREY = '\033[90m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
    '''list s3 bucket objects in a tree-like format.'''
    parser = argparse.ArgumentParser(
        description='list s3 bucket objects in a tree-like format.',
        prog='s3-tree',
        formatter_class=rawtxt
    )

    #parser.print_help()
    parser.add_argument(
        "bucket",
        help="""list s3 bucket objects in a tree-like format.\n
    $ s3-tree example\n
    where example is the bucket you wanna show.""",
        nargs='?',
        default='none'
    )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    bucket = args.bucket
    if bucket == "none":
        cmd = "aws s3 ls --output json"
        buckets = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        print(buckets)
        exit()
    else:
        try:
            if not is_tool("tree"):
                print(Bcolors.WARNING+"please install tree to use this program"+Bcolors.ENDC)
                exit()
            cmd = "aws s3api list-objects --bucket {} --output json"
            objects = subprocess.check_output(cmd.format(bucket), shell=True).decode("utf-8").strip()
            objects = json.loads(objects)
            objects = objects['Contents']
            home = expanduser('~')
            today = datetime.today().strftime('%Y-%m-%d')
            dl_path = home+"/delete-later-"+today+"/"+bucket
            if not os.path.exists(dl_path):
                os.makedirs(dl_path)
            else:
                print(Bcolors.WARNING+"for some weird reason "+dl_path+" exists already"+Bcolors.ENDC)
                exit()
            dl_path += "/"
            for obj in objects:
                key = obj['Key']
                if "/" in key:
                    keyarr = key.split("/")
                    dir2create = '/'.join(keyarr[:-1])
                    dir2create = dl_path+dir2create
                    if not os.path.exists(dir2create):
                        os.makedirs(dir2create)
                Path(dl_path+key).touch()
            dl_path = dl_path[:-1]
            dl_path_arr = dl_path.split("/")
            dir2change2 = '/'.join(dl_path_arr[:-1])
            dir2change2 = "/"+dir2change2
            os.chdir(dir2change2)
            os.system("tree "+bucket)
            # remove dl_path
            shutil.rmtree(dir2change2)
        except subprocess.CalledProcessError:
            print(Bcolors.WARNING+"{}: could not find bucket".format(bucket)+Bcolors.ENDC)
            exit()

if __name__ == "__main__":
    main()
