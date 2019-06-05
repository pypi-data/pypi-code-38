# cli.py - Command line interface for automation
#
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# no-check-code because Python 3 native.

import argparse
import os
import pathlib

from . import (
    aws,
    HGAutomation,
    windows,
)


SOURCE_ROOT = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent.parent
DIST_PATH = SOURCE_ROOT / 'dist'


def bootstrap_windows_dev(hga: HGAutomation, aws_region):
    c = hga.aws_connection(aws_region)
    image = aws.ensure_windows_dev_ami(c)
    print('Windows development AMI available as %s' % image.id)


def build_inno(hga: HGAutomation, aws_region, arch, revision, version):
    c = hga.aws_connection(aws_region)
    image = aws.ensure_windows_dev_ami(c)
    DIST_PATH.mkdir(exist_ok=True)

    with aws.temporary_windows_dev_instances(c, image, 't3.medium') as insts:
        instance = insts[0]

        windows.synchronize_hg(SOURCE_ROOT, revision, instance)

        for a in arch:
            windows.build_inno_installer(instance.winrm_client, a,
                                         DIST_PATH,
                                         version=version)


def build_wix(hga: HGAutomation, aws_region, arch, revision, version):
    c = hga.aws_connection(aws_region)
    image = aws.ensure_windows_dev_ami(c)
    DIST_PATH.mkdir(exist_ok=True)

    with aws.temporary_windows_dev_instances(c, image, 't3.medium') as insts:
        instance = insts[0]

        windows.synchronize_hg(SOURCE_ROOT, revision, instance)

        for a in arch:
            windows.build_wix_installer(instance.winrm_client, a,
                                        DIST_PATH, version=version)


def build_windows_wheel(hga: HGAutomation, aws_region, arch, revision):
    c = hga.aws_connection(aws_region)
    image = aws.ensure_windows_dev_ami(c)
    DIST_PATH.mkdir(exist_ok=True)

    with aws.temporary_windows_dev_instances(c, image, 't3.medium') as insts:
        instance = insts[0]

        windows.synchronize_hg(SOURCE_ROOT, revision, instance)

        for a in arch:
            windows.build_wheel(instance.winrm_client, a, DIST_PATH)


def build_all_windows_packages(hga: HGAutomation, aws_region, revision):
    c = hga.aws_connection(aws_region)
    image = aws.ensure_windows_dev_ami(c)
    DIST_PATH.mkdir(exist_ok=True)

    with aws.temporary_windows_dev_instances(c, image, 't3.medium') as insts:
        instance = insts[0]

        winrm_client = instance.winrm_client

        windows.synchronize_hg(SOURCE_ROOT, revision, instance)

        for arch in ('x86', 'x64'):
            windows.purge_hg(winrm_client)
            windows.build_wheel(winrm_client, arch, DIST_PATH)
            windows.purge_hg(winrm_client)
            windows.build_inno_installer(winrm_client, arch, DIST_PATH)
            windows.purge_hg(winrm_client)
            windows.build_wix_installer(winrm_client, arch, DIST_PATH)


def terminate_ec2_instances(hga: HGAutomation, aws_region):
    c = hga.aws_connection(aws_region)
    aws.terminate_ec2_instances(c.ec2resource)


def purge_ec2_resources(hga: HGAutomation, aws_region):
    c = hga.aws_connection(aws_region)
    aws.remove_resources(c)


def run_tests_windows(hga: HGAutomation, aws_region, instance_type,
                      python_version, arch, test_flags):
    c = hga.aws_connection(aws_region)
    image = aws.ensure_windows_dev_ami(c)

    with aws.temporary_windows_dev_instances(c, image, instance_type,
                                             disable_antivirus=True) as insts:
        instance = insts[0]

        windows.synchronize_hg(SOURCE_ROOT, '.', instance)
        windows.run_tests(instance.winrm_client, python_version, arch,
                          test_flags)


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--state-path',
        default='~/.hgautomation',
        help='Path for local state files',
    )
    parser.add_argument(
        '--aws-region',
        help='AWS region to use',
        default='us-west-1',
    )

    subparsers = parser.add_subparsers()

    sp = subparsers.add_parser(
        'bootstrap-windows-dev',
        help='Bootstrap the Windows development environment',
    )
    sp.set_defaults(func=bootstrap_windows_dev)

    sp = subparsers.add_parser(
        'build-all-windows-packages',
        help='Build all Windows packages',
    )
    sp.add_argument(
        '--revision',
        help='Mercurial revision to build',
        default='.',
    )
    sp.set_defaults(func=build_all_windows_packages)

    sp = subparsers.add_parser(
        'build-inno',
        help='Build Inno Setup installer(s)',
    )
    sp.add_argument(
        '--arch',
        help='Architecture to build for',
        choices={'x86', 'x64'},
        nargs='*',
        default=['x64'],
    )
    sp.add_argument(
        '--revision',
        help='Mercurial revision to build',
        default='.',
    )
    sp.add_argument(
        '--version',
        help='Mercurial version string to use in installer',
    )
    sp.set_defaults(func=build_inno)

    sp = subparsers.add_parser(
        'build-windows-wheel',
        help='Build Windows wheel(s)',
    )
    sp.add_argument(
        '--arch',
        help='Architecture to build for',
        choices={'x86', 'x64'},
        nargs='*',
        default=['x64'],
    )
    sp.add_argument(
        '--revision',
        help='Mercurial revision to build',
        default='.',
    )
    sp.set_defaults(func=build_windows_wheel)

    sp = subparsers.add_parser(
        'build-wix',
        help='Build WiX installer(s)'
    )
    sp.add_argument(
        '--arch',
        help='Architecture to build for',
        choices={'x86', 'x64'},
        nargs='*',
        default=['x64'],
    )
    sp.add_argument(
        '--revision',
        help='Mercurial revision to build',
        default='.',
    )
    sp.add_argument(
        '--version',
        help='Mercurial version string to use in installer',
    )
    sp.set_defaults(func=build_wix)

    sp = subparsers.add_parser(
        'terminate-ec2-instances',
        help='Terminate all active EC2 instances managed by us',
    )
    sp.set_defaults(func=terminate_ec2_instances)

    sp = subparsers.add_parser(
        'purge-ec2-resources',
        help='Purge all EC2 resources managed by us',
    )
    sp.set_defaults(func=purge_ec2_resources)

    sp = subparsers.add_parser(
        'run-tests-windows',
        help='Run tests on Windows',
    )
    sp.add_argument(
        '--instance-type',
        help='EC2 instance type to use',
        default='t3.medium',
    )
    sp.add_argument(
        '--python-version',
        help='Python version to use',
        choices={'2.7', '3.5', '3.6', '3.7', '3.8'},
        default='2.7',
    )
    sp.add_argument(
        '--arch',
        help='Architecture to test',
        choices={'x86', 'x64'},
        default='x64',
    )
    sp.add_argument(
        '--test-flags',
        help='Extra command line flags to pass to run-tests.py',
    )
    sp.set_defaults(func=run_tests_windows)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    local_state_path = pathlib.Path(os.path.expanduser(args.state_path))
    automation = HGAutomation(local_state_path)

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    kwargs = dict(vars(args))
    del kwargs['func']
    del kwargs['state_path']

    args.func(automation, **kwargs)
