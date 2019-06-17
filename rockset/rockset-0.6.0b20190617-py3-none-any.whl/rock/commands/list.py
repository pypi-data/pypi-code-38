from docopt import docopt

from .command_rest import RESTCommand
from .util.type_util import IntegrationType


class List(RESTCommand):
    @classmethod
    def what(cls):
        return ('ls', 'List all collections')

    def usage(self):
        return """
usage: rock list [-h] [<resource-type>]

List all collections, integrations, or workspaces.

arguments:
    <resource-type>       oneof collections, integrations or workspaces. Default: collections

Valid resource types:
  * collections (aka 'col')
  * integrations (aka 'int')
  * workspaces (aka 'ws')

options:
  -h, --help            show this help message and exit
        """

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args, help=False))

        # handle help
        if parsed_args['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        resource_type = parsed_args['<resource-type>']

        # check if list integrations
        if resource_type in ['c', 'col', 'collection', 'collections']:
            return {'resource': 'COLLECTIONS'}
        elif resource_type in ['i', 'int', 'integration', 'integrations']:
            return {'resource': 'INTEGRATIONS'}
        elif resource_type in ['w', 'ws', 'workspace', 'workspaces']:
            return {'resource': 'WORKSPACES'}
        elif resource_type is not None:
            ret = 'Error: invalid resource type "{}"\n'.format(resource_type)
            ret += self.usage()
            raise SystemExit(ret.strip())

        return {'resource': 'COLLECTIONS'}

    def go(self):
        if self.resource == 'INTEGRATIONS':
            return self.go_integrations()
        if self.resource == 'WORKSPACES':
            return self.go_workspaces()
        return self.go_collections()

    def go_collections(self):
        path = '/v1/orgs/{}/collections'.format('self')
        items = self.get(path)['data']
        for item in items:
            item['type'] = 'COLLECTION'
            item['size'] = item.get('stats', {}).get('total_size', 0)
        sorted_items = sorted(items, key=lambda k: k['type'] + ':' + k['workspace'] + ':' + k['name'])
        return (0, sorted_items)

    def go_integrations(self):
        path = '/v1/orgs/{}/integrations'.format('self')
        items = self.get(path)['data']
        for item in items:
            item['type'] = self.integration_type(item)
        sorted_items = sorted(items, key=lambda k: k['type'] + ':' + k['name'])
        return (0, sorted_items)

    def go_workspaces(self):
        path = '/v1/orgs/{}/ws'.format('self')
        items = self.get(path)['data']
        for item in items:
            item['type'] = 'WORKSPACE'
            item['is_empty'] = str(item['collection_count'] == 0)
        sorted_items = sorted(items, key=lambda k: k['type'] + ':' + k['is_empty'] + ':' + k['name'])
        return (0, sorted_items)

    def print_result(self, result):
        if self.resource == 'INTEGRATIONS':
            self.print_list(
                0, result, ['type', 'name', 'description', 'created_by']
            )
            return
        if self.resource == 'WORKSPACES':
            self.print_list(
                0, result, ['type', 'name', 'description', 'collection_count', 'created_by', 'created_at']
            )
            return
        self.print_list(
            0, result, ['name', 'workspace', 'status', 'description', 'created_by', 'created_at', 'size']
        )

    def integration_type(self, integration):
        if integration['dynamodb'] is not None:
            return IntegrationType.DYNAMODB
        elif integration['gcs'] is not None:
            return IntegrationType.GCS
        elif integration['kinesis'] is not None:
            return IntegrationType.KINESIS
        elif integration['redshift'] is not None:
            return IntegrationType.REDSHIFT
        elif integration['s3'] is not None:
            return IntegrationType.S3

        # deprecated
        elif integration['aws'] is not None:
            return IntegrationType.ACCESS_KEY
        elif integration['aws_external_id'] is not None:
            return IntegrationType.EXTERNAL_ID
        elif integration['gcp_service_account'] is not None:
            return IntegrationType.GCP_SERVICE_ACCOUNT

        else:
            return 'UNKNOWN'
