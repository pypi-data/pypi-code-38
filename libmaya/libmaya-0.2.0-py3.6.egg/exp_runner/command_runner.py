#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 00:03:52 2018

"""
import subprocess
import time 
import sys 
from shutil import copyfile
import os
import errno 
import shutil
 
def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


def run_command(command):
    result = []
    proc = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE)
    pid = proc.pid
    output = proc.stdout
    raw_report  = output.readlines()
    for line in raw_report:
        result.append(line.decode("utf-8"))
#    print("report," ,result)
    return result


def run_command_with_id(command_id,command):
    base_dir = os.path.abspath('./')
    dummy_path = '../'+str(command_id)+'/'
    if os.path.exists(dummy_path):
        shutil.rmtree(dummy_path)

    # os.makedirs(dummy_path)
    shutil.copytree('./', dummy_path)
    os.chdir(dummy_path)
    print("working in",dummy_path,command)
    result = run_command(command)
    # os.remove(dummy_path)
    os.chdir(base_dir)
    return result

if __name__ == '__main__':
    command = 'ls'
    result = run_command(command)