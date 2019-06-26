# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>
#            Qixiang Wan <qwan@redhat.com>

import argparse
import json
import logging
import os
import re
import sys
import six

from ursa_major.logger import log
from ursa_major.handlers.add_module import AddModuleHandler
from ursa_major.handlers.add_tag import AddTagHandler
from ursa_major.handlers.check_config import CheckConfigHandler
from ursa_major.handlers.remove_module import RemoveModuleHandler
from ursa_major.handlers.show_config import ShowConfigHandler

if six.PY3:  # SafeConfigParser == ConfigParser, former deprecated in >= 3.2
    from six.moves.configparser import ConfigParser
else:
    from six.moves.configparser import SafeConfigParser as ConfigParser

cli_name = os.path.basename(sys.argv[0])
cwd = os.getcwd()

DEFAULT_CONFIG_FILE = "/etc/ursa-major/%s.conf" % cli_name

DEFAULT_USER_CONFIG_FILE = os.path.join(
    os.path.expanduser('~'), '.config', 'ursa-major', '%s.conf' % cli_name)

DEFAULT_TAG_CONFIG_FILE = os.path.join(cwd, 'ursa-major.json')


def validate_json_file(value):
    if not os.path.exists(value):
        if value == DEFAULT_TAG_CONFIG_FILE:
            raise argparse.ArgumentTypeError(
                'Default tag config file ursa-major.json is not found from '
                'current directory.\n'
                'Make sure to run ursa-major alongside it, otherwise specify '
                'the file by option --tag-config-file.')
        else:
            raise argparse.ArgumentTypeError(
                'Specified tag config file does not exist: {}'.format(value))

    try:
        with open(value, 'r') as f:
            json.load(f)
    except IOError as e:
        raise argparse.ArgumentTypeError('Cannot read tag config file: {}'.format(str(e)))
    except Exception as e:
        raise argparse.ArgumentTypeError("Invalid json file {}: {}.".format(value, str(e)))
    return value


def clean_module_require(value):
    ore = re.compile(r'^(\w+):([-.\w]+)$')
    match = ore.match(value)
    if match:
        return match.groups()
    raise argparse.ArgumentTypeError('{} is not a pair of NAME:STREAM.'.format(value))


def main(args=None):
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(help="Sub commands", dest='subcommand')
    subparser.required = True

    global_args_parser = argparse.ArgumentParser(add_help=False)
    global_args_parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='dry run mode')
    global_args_parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='show debug log')
    global_args_parser.add_argument(
        '--config',
        metavar='PATH',
        default=DEFAULT_CONFIG_FILE,
        help='config file for ursa-major')
    global_args_parser.add_argument(
        '--user-config',
        metavar='PATH',
        default=DEFAULT_USER_CONFIG_FILE,
        help='user config file to use, can override default configurations')
    global_args_parser.add_argument(
        '--tag-config-file',
        metavar='PATH',
        default=DEFAULT_TAG_CONFIG_FILE,
        type=validate_json_file,
        help='tag config file, default to "ursa-major.json" in current working directory')
    global_args_parser.add_argument(
        '--traceback',
        action='store_true',
        default=False,
        help='Print traceback if something wrong that ursa-major cannot do the job.')

    module_config_parser = argparse.ArgumentParser(add_help=False)
    module_config_parser.add_argument(
        '--name',
        metavar='NAME',
        dest='module_name',
        required=True,
        help="module name (required)")
    module_config_parser.add_argument(
        '--stream',
        metavar='STREAM',
        dest='module_stream',
        required=True,
        help="module stream (required)")
    module_config_parser.add_argument(
        '--require',
        metavar='NAME:STREAM',
        type=clean_module_require,
        action='append',
        dest='module_requires',
        help='module runtime dependency in NAME:STREAM')
    module_config_parser.add_argument(
        '--buildrequire',
        metavar='NAME:STREAM',
        type=clean_module_require,
        action='append',
        dest='module_buildrequires',
        help='module build dependency in NAME:STREAM, for example platform:f30')

    show_config_parser = subparser.add_parser(
        "show-config",
        parents=[global_args_parser],
        help="show tag configuration content")
    show_config_parser.set_defaults(_class=ShowConfigHandler, func='run')
    show_config_parser.add_argument(
        '--tag',
        metavar='TAG',
        help="show config of this tag only")

    check_config_parser = subparser.add_parser(
        "check-config",
        parents=[global_args_parser],
        help="validate tag config file")
    check_config_parser.set_defaults(_class=CheckConfigHandler, func='run')
    check_config_parser.add_argument(
        '--allow-non-ready-module',
        action='store_true',
        default=False,
        help='allow non ready modules in config file')

    remove_module_parser = subparser.add_parser(
        "remove-module",
        parents=[global_args_parser, module_config_parser],
        help="remove a module config from a tag and also remove that module's "
             "koji_tag if it inherits from that tag.")
    remove_module_parser.set_defaults(_class=RemoveModuleHandler, func='run')
    remove_module_parser.add_argument(
        '--tag',
        metavar='TAG',
        required=True,
        help="a tag name (required). Specified module config will be removed "
             "if tag presents in tag config file and has the module config. "
             "The module's koji_tag will also be removed from tag inheritance "
             "if it inherits from this tag.")
    remove_module_parser.add_argument(
        '--not-update-config',
        action='store_true', default=False,
        help='do not update tag configuration file')

    add_module_parser = subparser.add_parser(
        'add-module',
        parents=[global_args_parser, module_config_parser],
        help="add a module to tag config file, find out the latest built "
             "module in MBS and add its tag to koji tag inheritance.")
    add_module_parser.set_defaults(_class=AddModuleHandler, func='run')
    add_module_parser.add_argument(
        '--tag',
        metavar='TAG',
        required=True,
        help="koji tag we operate against (required)")
    add_module_parser.add_argument(
        '--force',
        action='store_true',
        default=False,
        help="force to remove existing old koji tags from specified koji tag's "
             "inheritance data even there is no module build found in MBS for "
             "the specified module, and update config file as well")
    add_module_parser.add_argument(
        '--priority',
        type=int,
        required=True,
        help="priority of the module's koji tag in tag inheritance (required)")
    add_module_parser.add_argument(
        '--wait-regen-repo',
        action='store_true', default=False,
        help='wait for regen-repo task(s) to finish')
    mutual_args = add_module_parser.add_mutually_exclusive_group()
    mutual_args.add_argument(
        '--update-inheritance-only',
        action='store_true',
        default=False,
        help="only update the specified koji tag's inheritance data to add or "
             "edit the latest module build's tag, do not update tag configuration file")
    mutual_args.add_argument(
        '--update-config-only',
        action='store_true',
        default=False,
        help="only add the specified module into tag configuration file, do not "
             "update the specified koji tag's inheritance data")

    add_tag_parser = subparser.add_parser(
        "add-tag",
        parents=[global_args_parser],
        help="read module stage change message from an environment variable and "
             "add the module's tag to koji tag inheritance depending on the "
             "tag configuration")
    add_tag_parser.set_defaults(_class=AddTagHandler, func='run')
    add_tag_parser.add_argument(
        '--module-from-env',
        metavar='ENV_VAR',
        default='CI_MESSAGE',
        help="the environment variable contains the module state change message, "
             "default variable is 'CI_MESSAGE'")
    add_tag_parser.add_argument(
        '--send-mail',
        action='store_true', default=False,
        help='send mail after operations')
    add_tag_parser.add_argument(
        '--wait-regen-repo',
        action='store_true', default=False,
        help='wait for regen-repo task to finish')

    args = parser.parse_args(args)
    debug = getattr(args, 'debug', False)
    if debug:
        [h.setLevel(logging.DEBUG) for h in log.handlers]
        log.setLevel(logging.DEBUG)

    config = ConfigParser()
    sys_config = getattr(args, 'config', None)
    user_config = getattr(args, 'user_config', None)

    # read system config file
    if sys_config is not None:
        if os.path.exists(sys_config):
            log.info("Reading config from %s", sys_config)
            config.read(sys_config)
        else:
            log.error("Default ursa-major config file '%s' is missing", sys_config)
            sys.exit(1)

    # read user config file, which can overrides configurations
    # in system config file
    if user_config is not None and os.path.exists(user_config):
        log.info("Reading user config from %s", user_config)
        config.read(user_config)

    _class = args._class(config)
    _class.set_args(args)
    func = getattr(_class, args.func)
    try:
        func()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        if args.traceback:
            log.exception(str(e))
        else:
            log.error(str(e))
        sys.exit(1)
