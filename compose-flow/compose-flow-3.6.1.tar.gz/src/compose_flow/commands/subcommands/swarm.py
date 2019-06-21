#!/usr/bin/env python3
"""
Subcommand for working with the Docker Swarm


The `inspect` action will list all the services running on the swarm

```
compose-flow -e dev swarm inspect
```
"""
import argparse
import collections

from compose_flow import docker
from tabulate import tabulate

from .base import BaseSubcommand


# https://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
def flatten(d, parent_key='', sep='_'):
    items = []

    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k

        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


class Swarm(BaseSubcommand):
    setup_profile = False

    @classmethod
    def fill_subparser(cls, parser, subparser):
        subparser.epilog = __doc__
        subparser.formatter_class = argparse.RawDescriptionHelpFormatter

        subparser.add_argument('action', help='The action to run')

    def action_inspect(self):
        # for node in docker.get_nodes():
        #     print(node)

        service_status_l = []

        for service in docker.get_services():
            service_name = service['Name']
            service_status = {}

            service_info = {
                'service': {'name': service_name},
                'status': service_status,
            }

            service_config = docker.get_service_config(service_name)

            spec = service_config[0]['Spec']
            task_template = spec['TaskTemplate']

            # check placement constraints.  if the mode is global, the service should run on every available machine
            mode = spec['Mode']
            if 'Global' in mode:
                service_status['has_node_constraint'] = 'Global'
            else:
                placement_constraints = task_template['Placement'].get('Constraints', [])

                service_status['has_node_constraint'] = any([x.startswith('node.role') for x in placement_constraints])

            # check resources
            resources = task_template['Resources']

            service_status['has_limits'] = 'Limits' in resources
            service_status['has_reservations'] = 'Reservations' in resources

            service_status_l.append(service_info)

        flat_l = [flatten(x) for x in service_status_l]

        print(tabulate(flat_l, headers='keys'))
