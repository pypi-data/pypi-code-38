#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import colorama
import inspect
import sys
import os
from argparse import ArgumentError, ArgumentParser
from sesame.commands.new import new_cmd
from sesame.commands.build import build_cmd
from sesame.commands.dbuild import dbuild_cmd

class Command(object):
    def __init__(self):
        pass

    def help(self, *args):
        print('Display Help')

    def new(self, *args):
        new_cmd(args)

    def build(self, *args):
        build_cmd(args)

    def dbuild(self, *args):
        dbuild_cmd(args)

    def _commands(self):
        result = {}
        for m in inspect.getmembers(self, predicate=inspect.ismethod):
            method_name = m[0]
            if not method_name.startswith('_'):
                method = m[1]
                result[method_name.replace('_', '-')] = method
        return result

    def _run(self, args):
        if args:
            commands = self._commands()
            if args[0] in commands:
                command = args[0]
                method = commands[command]
                method(args[1:])
            else:
                print("No command given.")

def _main(args):
    colorama.init(autoreset=True)
    command = Command()
    command._run(args)

def run():
    _main(sys.argv[1:])

if __name__ == '__main__':
    run()
