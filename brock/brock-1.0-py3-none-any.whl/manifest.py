#!/usr/bin/env python3

"""
Support for provisioning blueprint constellations via a provided manifest.

Usage: manifest [-m <manifest_file>] <apply|destroy>

e.g.

* manifest example.yml apply
* manifest destroy # use file "manifest.yml" in current directory
"""
import argparse
import os
from os.path import expanduser

import docker
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def init_path(path):
    os.makedirs(expanduser(f'~/.bedrock/{path}'), exist_ok=True)


def parse_manifest(file):
    return yaml.load(file, Loader=Loader)


def resolve_key(parts, varlist, default_key):
    varmap = dict(map(lambda var: var.split('='), varlist))
    keyparts = [key for key in (map(lambda part: varmap[part] if part in varmap else None, parts) if parts else None) if key is not None]
    return f'{"-".join(keyparts)}' if keyparts else default_key


def append_env(environment, env_var):
    if env_var in os.environ:
        environment.append(f'{env_var}={os.environ[env_var]}')


def apply_blueprint(name, key, config, action, extra_volumes, extra_config):
    print(f'Apply blueprint: {name}/{key} [{action}]')

    init_path(f'{name}/{key}')

    client = docker.from_env()
    environment = [
        f'TF_BACKEND_KEY={name}/{key}',
        f'AWS_ACCESS_KEY_ID={os.environ["AWS_ACCESS_KEY_ID"]}',
        f'AWS_SECRET_ACCESS_KEY={os.environ["AWS_SECRET_ACCESS_KEY"]}',
        f'AWS_DEFAULT_REGION={os.environ["AWS_DEFAULT_REGION"]}',
    ]

    # Append optional environment variables..
    for env_var in ['AWS_SESSION_TOKEN', 'TF_APPLY_ARGS', 'TF_PLAN_ARGS', 'TF_DESTROY_ARGS',
                    'http_proxy', 'https_proxy', 'no_proxy']:
        append_env(environment, env_var)

    if config:
        for item in config:
            if isinstance(config[item], list):
                config_string = '["%s"]' % '","'.join(config[item])
                environment.append(f'TF_VAR_{item}={config_string}')
            else:
                environment.append(f'TF_VAR_{item}={config[item]}')

    if extra_config:
        for cnf in extra_config:
            cargs = cnf.split('=')
            environment.append(f'TF_VAR_{cargs[0]}={cargs[1]}')

    volumes = {
        expanduser(f'~/.bedrock/{name}/{key}'): {
            'bind': '/work',
            'mode': 'rw'
        }
    }

    if extra_volumes:
        for volume in extra_volumes:
            vargs = volume.split(':')
            volumes[vargs[0]] = {
                'bind': vargs[1],
                'mode': 'ro'
            }

    container = client.containers.run(f"bedrock/{name}", action, privileged=True, network_mode='host',
                          remove=True, environment=environment, volumes=volumes, tty=True, detach=True)
    logs = container.logs(stream=True)
    for log in logs:
        print(log.decode('utf-8'), end='')


def apply_blueprints(tf_key, blueprints, action, volumes, config):
    for blueprint in blueprints:
        apply_blueprint(blueprint, tf_key, blueprints[blueprint], action, volumes, config)


def main():
    parser = argparse.ArgumentParser(description='Bedrock Manifest Tool.')
    parser.add_argument('-m', '--manifest', metavar='<manifest_path>', default='manifest.yml', type=argparse.FileType('r'),
                        help='location of manifest file (default: %(default)s)')
    parser.add_argument('-v', '--volumes', metavar='<path:volume>', nargs='+',
                        help='additional volumes mounted to support blueprints')
    parser.add_argument('-c', '--config', metavar='<key=value>', nargs='+',
                        help='additional configuration to support blueprints')
    parser.add_argument('action', metavar='<command>', choices=['init', 'apply', 'plan', 'destroy'],
                        help='manifest action (possible values: %(choices)s)', nargs='?', default='init')

    args = parser.parse_args()

    manifest = parse_manifest(args.manifest)
    constellations = manifest['constellations']

    if args.action == 'destroy':
        # destroy in reverse order..
        constellations = constellations[::-1]

    for constellation in constellations:
        constellation_key = None
        blueprints = None
        if 'keyvars' in manifest['constellations'][constellation]:
            constellation_key = resolve_key(manifest['constellations'][constellation]['keyvars'],
                                            args.config, constellation)
            # blueprints = {k:v for (k,v) in manifest['constellations'][constellation].items() if k != 'keyvars'}
            blueprints = manifest['constellations'][constellation]['blueprints']
        else:
            constellation_key = constellation
            blueprints = manifest['constellations'][constellation]

        if args.action == 'destroy':
            # destroy in reverse order..
            blueprints = blueprints[::-1]

        apply_blueprints(constellation_key, blueprints, args.action, args.volumes, args.config)


if __name__ == "__main__":
    main()
