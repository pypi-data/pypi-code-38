# -*- coding: utf-8 -*-
"""Print system information useful for bug reports or other inspections."""

import platform
import sys
from os import environ

import click

from pype.constants import ENV_CONFIG_FILE
from pype.core import fname_to_name

from tabulate import tabulate


@click.command(name=fname_to_name(__file__), help=__doc__)
def main():
    """Script's main entry point."""
    unset = 'Not set'
    print('PYPE SYSTEM ENVIRONMENT')
    infos = []
    infos.append(['MACHINE', platform.machine()])
    infos.append(['PROCESSOR', platform.processor()])
    infos.append(['PLATFORM', platform.platform()])
    infos.append(['VERSION', platform.version()])
    infos.append(['RELEASE', platform.release()])
    infos.append(['SYSTEM', platform.system()])
    infos.append(['PY VERSION', sys.version])
    infos.append(['PY VERSION_INFO', sys.version_info])
    infos.append(['SHELL', environ.get('SHELL', unset)])
    infos.append(['CONFIG FILE', environ.get(ENV_CONFIG_FILE, unset)])
    print(tabulate(infos))
