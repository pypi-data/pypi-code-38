from .command_rest import RESTCommand
from .util.type_util import TypeUtil
from .util.parse_util import parse_collection_path

from docopt import docopt


class Describe(RESTCommand):
    def usage(self):
        return """
usage: rock describe [-ah] <resource-type> <name> ...

Show details about collections or integrations.

arguments:
    <name>                name of the collection or integration
    <resource-type>       oneof collections or integrations.

Valid resource types:
  * collections (aka 'col')
  * integrations (aka 'int')
  * workspaces (aka 'ws')

options:
    -a, --all           display extended stats
    -h, --help          show this help message and exit"""

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args))
        if parsed_args['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        resource_type = TypeUtil.parse_resource_type(
            parsed_args['<resource-type>']
        )
        if resource_type is None:
            ret = 'Error: invalid resource type "{}"\n'.format(resource_type)
            ret += self.usage()
            raise SystemExit(ret.strip())
        return {
            "resource": {
                'type': resource_type,
                'name': parsed_args['<name>']
            }
        }

    def go(self):
        self.logger.info('describe {}'.format(self.resource))
        if self.resource["type"] == TypeUtil.TYPE_COLLECTION:
            return self.go_collection()
        elif self.resource["type"] == TypeUtil.TYPE_INTEGRATION:
            return self.go_integration()
        elif self.resource["type"] == TypeUtil.TYPE_WORKSPACE:
            return self.go_workspace()
        else:
            return 1

    def go_collection(self):
        for name in self.resource['name']:
            workspace, collection_name = parse_collection_path(name)
            path = '/v1/orgs/{}/ws/{}/collections/{}'.format(
                'self', workspace, collection_name
            )
            deets = self.get(path)
            if deets.get('sources', None) is not None:
                nsrcs = []
                for src in deets['sources']:
                    nsrcs.append({k: v for k, v in src.items() if v})
                deets['data']['sources'] = nsrcs
            desc = {}
            if deets.get('data', None) is not None:
                desc = {k: v for k, v in deets['data'].items() if v}
            self.print_list(0, [desc], default='yaml')
        return 0

    def go_integration(self):
        for name in self.resource['name']:
            path = '/v1/orgs/{}/integrations/{}'.format('self', name)
            response = self.get(path)
            if response.get('collections', None) is not None:
                nsrcs = []
                for src in response['collections']:
                    nsrcs.append({k: v for k, v in src.items() if v})
                response['data']['collections'] = nsrcs
            desc = {}
            if response.get('data', None) is not None:
                desc = {k: v for k, v in response['data'].items() if v}
            self.print_list(0, [desc], default='yaml')
        return 0

    def go_workspace(self):
        for name in self.resource['name']:
            path = '/v1/orgs/{}/ws/{}'.format('self', name)
            response = self.get(path)
            desc = {}
            if response.get('data', None) is not None:
                desc = {k: v for k, v in response['data'].items() if v}
            self.print_list(0, [desc], default='yaml')
        return 0
