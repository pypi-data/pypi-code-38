#!/usr/bin/env python3

import os
import argparse
import shutil
import json
from subprocess import check_call

from jinja2 import Environment, FileSystemLoader

def render(name, tmp_dir, config, env):
    template = env.get_template(name)

    with open(tmp_dir + "/" + name, "w") as f:
        f.write(template.render(data = config))

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(description='ROS 2 Docker Environment.')
    add = parser.add_argument
    add('positional', choices=['generate', 'build', 'env', 'run'])
    add('-p', '--project_name', default='myproject', help='docker project name')
    add('-d', '--output_dir', default=cwd + "/generated", help='Directory to hold generated files')
    add('-b', '--build_context', default=cwd, help='Docker build context')
    add('-u', '--user_name', default='ros2', help='User to create in Docker')
    add('-w', '--ws_copy_dir', default=None, help='Directory to copy into ROS 2.0 workspace')
    add('-c', '--command', default=None, help='Command to run')
    add('-o', '--dockerfile_override', default=None, help='Dockerfile that overrides base Dockerfile')
    add('-s', '--services_override', default=None, help='services that overrides base services')
    add('-r', '--ros_distro', default='dashing', help='The ROS distribution')

    args = parser.parse_args()

    config = {}
    config['Dockerfile'] = 'Dockerfile'
    config['docker-compose.yml'] = 'docker-compose.yml'
    config['services'] = 'services'
    config['ros_distro'] = args.ros_distro
    template_dirs = [script_dir + '/templates']

    if args.dockerfile_override is not None:
        config['Dockerfile'] = os.path.basename(args.dockerfile_override)
        template_dirs.append(os.path.dirname(os.path.realpath(args.dockerfile_override)))

    if args.services_override is not None:
        config['services'] = os.path.basename(args.services_override)
        template_dirs.append(os.path.dirname(os.path.realpath(args.services_override)))

    file_loader = FileSystemLoader(template_dirs)
    env = Environment(loader=file_loader)

    if not os.path.exists(args.output_dir):
        try:
            os.mkdir(args.output_dir)
        except OSError:
            print ("Creation of the directory %s failed" % args.output_dir)

    json_file = args.output_dir + "/config.json"

    if args.positional == 'generate':
        config['tmp_dir'] = args.output_dir
        config['USER_ID'] = os.geteuid()
        config['target'] = 'amd64'
        config['project_name'] = args.project_name
        config['build_context'] = args.build_context
        config['user_name'] = args.user_name
        config['ws_copy_dir'] = args.ws_copy_dir

        # Write the generate variables to a JSON file
        with open(json_file, "w") as f:
            f.write(json.dumps(config))

        # Render the templates
        render(config['Dockerfile'], config['tmp_dir'], config, env)
        render(config['docker-compose.yml'], config['tmp_dir'], config, env)
        return 0

    # Read in the configuration variables that were written during the generate
    # step.
    try:
        with open(json_file) as f:
            config = json.load(f)
    except:
        print("Failed to read config.json file at %s" % json_file)
        print("Did you skip the 'generate' step?")
        return -1

    if args.positional == 'build':
        cmd = "docker-compose -f " + config['docker-compose.yml'] + " -p " + config['project_name'] + " build " + config['target'] + "-" + config['project_name']
    elif args.positional == 'env':
        cmd = "docker-compose -f " + config['docker-compose.yml'] + " -p " + config['project_name'] + " up -d " + config['target'] + "-" + config['project_name'] + \
              " && docker attach " + config['project_name'] + "_" + config['target'] + "-" + config['project_name'] + "_1"
    elif args.positional == 'run':
        if args.command is not None:
            cmd = "docker run -it " + config['target'] + "/" + config['project_name'] + ":latest " + args.command
        else:
            print("When using the 'run' command, set the --command (-c) flag.")
            return -1

    check_call(cmd, cwd=config['tmp_dir'], shell=True)

    return 0

if __name__ == "__main__":
    sys.exit(main())
