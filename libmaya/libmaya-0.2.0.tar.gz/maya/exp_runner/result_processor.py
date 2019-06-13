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
 

def get_n_space(n):
    space = ''
    for i in range(n):
        space += '-'
    return space

def getCurrentDate():
    strDate = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())) 
    return strDate


def result_print(result_list,depth=0): 
    depth +=1
    if type(result_list) == list and len(result_list)!=1:
        for i,result in enumerate(result_list):
            space = get_n_space(depth)
            print("{}{}:".format(space,depth))
            result_print(result,depth)
    elif type(result_list) == list and len(result_list)==1:
        space = get_n_space(depth)
        print(space+result_list[0])
    elif len(result_list)!=0:
        space = get_n_space(depth)
        print(space+result_list)
        
def result_to_file(result_list):
    sys.stdout = open('run_log_{}.txt'.format(getCurrentDate()), 'w')
    result_print(result_list)

def result_to_file_read(result_list):
    sys.stdout = open('run_log_{}.txt'.format(getCurrentDate()), 'w')
    for inpu,outpu in result_list:
        print("input tuple:")
        print(inpu)
        print("output tuple:")
        print(outpu)

def result_to_file_raw(result_list):
    sys.stdout = open('run_log_{}.txt'.format(getCurrentDate()), 'w')
    for line in result_list:
        print(line)


if __name__ == '__main__':
    command = 'ls'