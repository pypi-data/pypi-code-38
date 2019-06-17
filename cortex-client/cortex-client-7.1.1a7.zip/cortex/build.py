"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys
from cortex import Cortex
import argparse
import yaml
from .exceptions import BuilderException


class ActionBuildCommand:
    """
    Builds a Cortex action.
    """
    def __init__(self, args):
        parser = argparse.ArgumentParser(description='Build and deploy a Cortex Action',
                                         usage='cortex-build actions [args] [action_name]')
        parser.add_argument('-f', '--file', type=open, default='project.yml')
        parser.add_argument('action_name', nargs='?', type=str)

        opts = parser.parse_args(args)
        project = yaml.load(opts.file)

        c = Cortex.client()
        b = c.builder()

        for action in project.get('actions', []):
            build = action.get('build', {})
            if build.get('runtime') == 'python3':
                action_name = action.get('name')
                # If action_name was specified, only build the requested action
                if opts.action_name:
                    if action_name != opts.action_name:
                        continue

                print('Building action: {}'.format(action_name))
                builder = b.action(action_name)

                # Action type: job, daemon
                action_type = action.get('type')
                if action_type and hasattr(builder, action_type):
                    getattr(builder, action_type)()

                if 'from_image' in build:
                    builder.from_image(build['from_image'])

                elif 'from_setup' in build:
                    s = build.get('from_setup')
                    setup_script = s.get('setup_script', 'setup.py')

                    if 'module' not in s:
                        raise BuilderException('from_setup requires the module to be specified')

                    if 'function' not in s:
                        raise BuilderException('from_setup requires the module to be specified')

                    builder.from_setup(setup_script, s['module'], s['function'])

                if 'requirements' in build:
                    builder.with_requirements(build['requirements'])

                if 'base_image' in build:
                    builder.with_base_image(build['base_image'])

                kwargs = build.get('extra', {})
                builder.build(**kwargs)


class CortexBuild:
    """
    Provides build functionality for the Cortex SDK.
    """
    def __init__(self):
        parser = argparse.ArgumentParser(description='Cortex Build Tool for Python', usage='cortex-build <command>')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        opts = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, opts.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, opts.command)()

    def actions(self):
        """
        Invokes ActionBuildCommand
        """
        ActionBuildCommand(sys.argv[2:])


def main():
    """
    Main function for invoking CortexBuild.
    """
    CortexBuild()
