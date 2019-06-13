#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Muduo
'''
    Fast Sync
'''
import sys
import argparse
from . import sender
from . import receiver

def print_version():
    print('''\033[32m
            + ------------------------------------------ +
            |           FastSync 0.2.0 is free         |
            + ------------------------------------------ +
            |                                            |
            |    ☺  -------------------------->  ☺       |
            |                                            |
            |   You could donate to the Alipay account   |
            |                                            |
            |            49668929@qq.com                 |
            |                                            |
            |         ~~~~Thank you!~~~~~~~              |
            |                                            |
            |            Author : Muduo                  |
            |                                            |
            + ------------------------------------------ +
    \033[0m''')

def sending():
    print_version()
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',
                        dest='send_path',
                        action='store',
                        help='sending local path like /home/work/workspace')
    parser.add_argument('-r',
                        dest='receive_uri',
                        action='store',
                        help='receiving uri like http://127.0.0.1:8888/home/work/workspace')
    parser.add_argument('-k',
                        dest='secret_key',
                        action='store',
                        help='secret key',
                        default='sync')
    parser.add_argument('-i',
                        dest='patterns',
                        action='store',
                        help='ignore sync filepath pattern',
                        default=['.git', '.svn'],
                        nargs='+')

    args = parser.parse_args()
    sender.sending(args.send_path, args.receive_uri, args.secret_key, args.patterns)

def receiving():
    print_version()
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',
                        dest='port',
                        action='store',
                        help='receiving service port',
                        default=8500)
    parser.add_argument('-s',
                        dest='secret_key',
                        action='store',
                        help='secret key',
                        default='sync')
    
    args = parser.parse_args()
    receiver.receiving(args.port, args.secret_key)
