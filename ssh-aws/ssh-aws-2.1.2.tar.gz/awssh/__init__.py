#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from os import path, system
from pprint import pprint
import argparse
import itertools
from collections import deque
import time

VERSION = "2.1.2"


def connect(instance, args):
    details = get_details(instance)
    print('\nConnecting to: {name}\n'.format(**details))
    pprint(details)

    if args.console_output:
        print('\n========= console output start =========')
        print(instance.console_output().get('Output', '').replace('\\n', '\n'))
        print('========== console output end ==========\n')

    users = deque(args.users)
    # return code 65280 is 'Permission Denied'
    while _connect(users.popleft(), instance, args) == 65280 and len(users):
        pass


def _connect(user, instance, args):
    config = {
        'key_path': get_key_path(args, instance),
        'tunnel': get_tunnel(args),
        'host': "{}@{}".format(user, instance.public_ip_address),
        'timeout': args.timeout
    }
    command = 'ssh -A -i {key_path} {tunnel} {host} -o ConnectTimeout={timeout}'.format(**config)

    if args.command:
        command = "{} -C '{}'".format(command, args.command)

    print('\nTrying with user: {}.\nCommand: {}'.format(user, command))
    return system(command)


def jump_connect(ssh_instance, jump_server, args):
    details_ssh_instance = get_details(ssh_instance)
    details_jump_server = get_details(jump_server)
    print('\nForce pseudo-tty allocation. \n'
          'Connecting to {} via {}: \n'.format(details_ssh_instance.get('name'), details_jump_server.get('name')))
    pprint(details_ssh_instance)

    if args.console_output:
        print('\n========= console output start =========')
        print(instance.console_output().get('Output', '').replace('\\n', '\n'))
        print('========== console output end ==========\n')

    users = deque(args.users)
    # return code 65280 is 'Permission Denied'
    while _jump_connect(users.popleft(), ssh_instance, jump_server, args) == 65280 and len(users):
        time.sleep(1)
    return True


def _jump_connect(user, ssh_instance, jump_server, args):
    command_tuple = {
        'key_path': get_key_path(args, jump_server),
        'tunnel': get_tunnel(args),
        'host': "{}@{}".format(user, jump_server.public_ip_address),
        'timeout': args.timeout,
        'ssh_instance': ssh_instance
    }
    command = 'ssh -A -i {key_path} {tunnel} {host} -o ConnectTimeout={timeout} -t ssh {ssh_instance.private_ip_address}'.format(**command_tuple)

    if args.command:
        command = "{} -C '{}'".format(command, args.command)

    print('\nTrying with user: {}.\nCommand: {}'.format(user, command))
    return system(command)


def get_tunnel(args):
    if not args.remote_host:
        return ''

    url = args.remote_host.split(':')
    if len(url) == 2:
        params = {'local_port': args.local_port or url[1], 'remote_host': url[0], 'remote_port': url[1]}
    elif len(url) == 3:
        params = {'local_port': url[0], 'remote_host': url[1], 'remote_port': url[2]}
    else:
        if not args.local_port:
            args.local_port = args.remote_port
        params = args.__dict__
    return "-L '{local_port}:{remote_host}:{remote_port}'".format(**params)


def get_details(instance):
    return {
        'id': instance.id,
        'name': get_name(instance),
        'type': instance.instance_type,
        'private_ip_address': instance.private_ip_address,
        'public_ip_address': instance.public_ip_address,
        'availability_zone': instance.placement.get('AvailabilityZone'),
        'security_groups': instance.security_groups,
        'state': instance.state.get('Name'),
        'launch time': instance.launch_time.isoformat(),
        'block devices': get_device_mappings(instance),
        'key_name': instance.key_name.replace(" ", "")
    }


def get_key_path(args, instance):
    if args.key_path:
        return args.key_path
    else:
        directory = path.expanduser(args.keys)
        return path.join(directory, instance.key_name.replace(" ", "") + '.pem')


def get_device_mappings(instance):
    return flatten([device.values() for device in instance.block_device_mappings])


def flatten(array):
    list(itertools.chain.from_iterable(array))


def get_name(instance):
    name = [tag for tag in instance.tags if tag['Key'] == 'Name']
    if not name or 'Value' not in name[0]:
        return 'not-named'
    return name[0].get('Value')


def get_instances(args):
    ec2 = boto3.resource('ec2', region_name=args.region)
    filters = [
        {'Name': 'tag:Name', 'Values': ['*{filter}*'.format(**args.__dict__)]},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ]

    print('Querying AWS for EC2 instances in region: {region}...\n'.format(**args.__dict__))
    return sorted(ec2.instances.filter(Filters=filters), key=get_name)


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        print(VERSION)
        exit(0)

    instances = get_instances(args)
    display_instances(instances)

    if not instances:
        print('No running instances found.\n')
        exit(1)

    if len(instances) == 1:
        print('Found one running instance and connecting to it...\n')
        connect(instances[0], args)
    else:
        select_instance(args, instances, parser)


def display_instances(instances):
    table_col_names = ['Name', 'Instance ID', 'Public IP',
                       'Private IP', 'Zone', 'Key Name']
    print("     {:<30}{:<21}{:<17}{:<17}{:<14}{}".format(*table_col_names))

    details_fmt = "{:2} - {name:<30}{id:<21}{public_ip_address:<17}" \
                  "{private_ip_address:<17}{availability_zone:<14}{key_name}"

    for i, instance in enumerate(instances):
        print(details_fmt.format(i, **get_details(instance)))
    print('')


def select_instance(args, instances, parser):
    connection = False
    try:
        server_selection = [int(x) for x in raw_input("Enter server number: ").split()]  # User selection
        if len(server_selection) == 1:
            if instances[server_selection[0]].public_ip_address is None:
                for instance in instances:
                    if instance.key_name == instances[server_selection[0]].key_name and instance.public_ip_address is not None:
                        # ssh_instance, jump_server, args
                        if jump_connect(instances[server_selection[0]], instance, args):
                            connection = True
                            break

                if connection:
                    exit(0)
                else:
                    print("No jump servers with the same 'Key Name' were found.\n"
                          "You can input two instances to jump from <a> to <b>.\n"
                          "e.g.:\n"
                          "\tEnter server number: {} {}\n".format((server_selection[0] + 5),
                                                                  server_selection[0]))
            else:
                connect(instances[server_selection[0]], args)
        elif len(server_selection) == 2:
            # server_selection[0] -- jump server
            # server_selection[1] -- target server
            if instances[server_selection[0]].public_ip_address is None:
                print("The provided jump server has no public IP address.\n"
                      "You can input two instances to jump from a to b.\n"
                      "However, the jump server needs to be reachable.\n"
                      "e.g.:\n"
                      "\tEnter server number: {} {}\n".format((server_selection[0] + 5), server_selection[0]))
                exit(0)
            else:
                jump_connect(instances[server_selection[1]], instances[server_selection[0]], args)
        else:
            print('Invalid number of instances.\n')
            exit(0)

    except ValueError:
        print('Invalid instance.\n')
        parser.print_help()

    except (EOFError, KeyboardInterrupt, SyntaxError):
        exit(0)


def create_parser():
    parser = argparse.ArgumentParser(description="""
          SSH into AWS instances.
          The default user list assumes that your user is centos, ubuntu, or ec2-user.

          ex: "awssh --users user1 user2 --region us-west-2 --keys '~/.keys' instance-name".

          Note that "awssh --users user1 user2 instance-name" will not be parsed properly
          due to the nature of nargs. In that case you may want to do:
          "awssh instance-name --users user1 user2".
          """)
    parser.add_argument('filter', nargs='?', default='*', help='Optional instance name or key word as a filter. '
                                                               'If only one instance is found, it will connect to it '
                                                               'directly.')
    parser.add_argument('--users', nargs='+', help='Users to try (centos, ubuntu, and ec2-user are defaults).',
                        default=['centos', 'ubuntu', 'ec2-user'])
    parser.add_argument('--region', help='AWS region (us-east-1 by default).', default='us-east-1')
    parser.add_argument('-i', '--key-path', help='Specific key path, overrides, --keys')
    parser.add_argument('-c', '--command', help='Translates to ssh -C')
    parser.add_argument('-r', '--remote-host',
                        help='Open a tunnel. '
                             'Equivalent to ssh -L <local-port>:<remote-host>:<remote-port> '
                             '<selected-aws-host>')
    parser.add_argument('-p', '--remote-port', help='Port to use on the remote host.', default=5432)
    parser.add_argument('-l', '--local-port',
                        help='Port to use on the local host. Get overwritten by remote port if not defined.')
    parser.add_argument('--keys', help='Directory of the private keys (~/.ssh by default).', default='~/.ssh/')
    parser.add_argument('--timeout', help='SSH connection timeout.', default='5')
    parser.add_argument('--console-output', help='Display the instance console out before logging in.',
                        action='store_true')
    parser.add_argument('--version', help='Returns awssh\'s version.', action='store_true')
    return parser


if __name__ == '__main__':
    main()
