from rockset import Client
from .command_rest import RESTCommand

from docopt import docopt

import json
import os
import sys
import yaml


class SetState(RESTCommand):
    def usage(self):
        return """
usage: rock setstate --help
       rock setstate <collection> <state>

Set the state of a collection to either READY or PAUSED

arguments for `rock setstate`:
  <collection>      name of the collection you wish to add data
  <state>           "READY" or "PAUSED"

options for `rock setstate`:
  -h, --help                show this help message and exit

examples:

    Set the state of a collection to READY:
        $ rock setstate my-collection READY

    Set the state of a collection to PAUSED
        $ rock setstate my-collection PAUSED

        """

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args, help=False))
        if parsed_args['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        params = {}

        if parsed_args['<collection>']:
            params['collection'] = parsed_args['<collection>']

        if parsed_args['<state>']:
            params['state'] = parsed_args['<state>'].upper()
        print(params)

        return {'params': params}

    def go(self):
        path = '/v1/orgs/{}/ws/{}/collections/{}/state/{}'.format(
            'self', 'commons', self.params['collection'], self.params['state']
        )

        deets = self.post(path)
        if 'sources' in deets:
            nsrcs = []
            for src in deets['sources']:
                nsrcs.append({k: v for k, v in src.items() if v})
            deets['data']['sources'] = nsrcs
        desc = {}
        if 'data' in deets:
            desc = {k: v for k, v in deets['data'].items() if v}
        self.print_list_yaml(0, [desc])
        return 0
