#!/usr/bin/env python3
#
# Copyright(C) 2019 wuyaoping
#

import sys
import click
import argparse
import subprocess
from subprocess import PIPE


def purge(package, verify):
    requires_pack = find_requires(package)
    if requires_pack == -1:
        return

    requires_pack_copy = requires_pack[:]
    while True:
        if not requires_pack_copy:
            break
        child_requires = find_requires(requires_pack_copy.pop())
        if child_requires:
            requires_pack.extend(child_requires)

    remove_pack = requires_pack
    remove_pack.append(package)
    print(','.join(["'%s'"%one for one in remove_pack]), 'will be removed!')

    if not verify:
        while True:
            option = input('Remove all or one-by-one? (y/o/n)')
            if option.lower() in ['y', 'o', 'n']:
                break
        if option.lower() == 'n':
            return
        elif option.lower() == 'o':
            pip_args = ['pip3', 'uninstall', 'pack_placeholder']
        else:
            pip_args = ['pip3', 'uninstall', '-y', 'pack_placeholder']

        for pack in remove_pack:
            pip_args[-1] = pack
            pip = subprocess.Popen(pip_args)
            pip.wait()
    else:
        for pack in remove_pack:
            pip = subprocess.Popen(['pip3', 'uninstall', '-y', pack])
            pip.wait()


def find_requires(package):
    show = subprocess.Popen(['pip3', 'show', package], stdout=PIPE)
    result = show.communicate()[0].decode()
    if not result:
        click.secho("ERROR: No package '%s' exist."%package, fg='red')
        return -1

    requires_str = result.strip().split('\n')[-2]
    requires_pack = [one.strip().lower() for one in requires_str.strip().split(':')[-1].split(',') if one.strip()]

    if requires_pack:
        all_packages = requires_pack[:]
        all_packages.append(package)

        for pack in requires_pack[:]:
            show = subprocess.Popen(['pip3', 'show', pack], stdout=PIPE)
            result = show.communicate()[0].decode()

            requires_str = result.strip().split('\n')[-1]
            another_req = [one.strip().lower() for one in requires_str.strip().split(':')[-1].split(',') if one.strip()]
            if another_req:
                for one in another_req:
                    if one not in all_packages:
                        requires_pack.remove(pack)
                        break
    
    return requires_pack


def parse_argument():
    parser = argparse.ArgumentParser(prog='pip-purge')

    parser.add_argument('packages', nargs='*', 
                        help='Input a list of packages.')
    parser.add_argument('-y', '--yes', action='store_true', 
                        help="Don't ask for confirmation of uninstall deletions.")

    return parser.parse_args()


def main():
    args = parse_argument()
    if args.packages:
        for package in args.packages:
            purge(package, args.yes)
    else:
        click.secho('Please input package(s) name.', fg='green')


if __name__ == '__main__':
    main()
