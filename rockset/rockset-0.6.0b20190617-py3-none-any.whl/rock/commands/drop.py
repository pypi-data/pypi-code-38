from .command_auth import AuthCommand
from .util.type_util import TypeUtil
from .util.parse_util import parse_collection_path
from docopt import docopt
from rockset.exception import InputError

class Drop(AuthCommand):
    def usage(self):
        return """
usage:
  rock delete --help
  rock delete [-h] --file=YAML_CONFIG_FILE
  rock delete <resource-type> <name> ...

arguments:
    <resource-type>          oneof collections, integrations, or workspaces.
    <name>                   name of the collection/integration/workspace to be dropped

Valid resource types:
  * collections (aka 'col')
  * integrations (aka 'int')
  * workspaces (aka 'ws')

options:
    -f, --file=<YAML configuration file>    drop all resources defined in the YAML file
    -h, --help                              show this help message and exit
        """

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args))

        # handle file option
        fn = parsed_args['--file']
        if fn:
            parsed = self._parse_yaml_file(fn)
            self.set_batch_items('resource', parsed)
            return {}

        resource_type = TypeUtil.parse_resource_type(parsed_args['<resource-type>'])
        if resource_type is None:
            ret = 'Error: invalid resource type "{}"\n'.format(resource_type)
            ret += self.usage()
            raise SystemExit(ret.strip())

        if len(parsed_args['<name>']) > 1:
            resources = [{'name': n, 'type': resource_type} for n in parsed_args['<name>']]
            self.set_batch_items('resource', resources)
            return {}

        name = {'name': parsed_args['<name>'].pop()}
        return {"resource": {'type': resource_type, **name}}

    def go(self):
        self.logger.info('drop {}'.format(self.resource))
        if self.resource["type"] == TypeUtil.TYPE_COLLECTION:
            return self.go_collection()
        elif self.resource["type"] == TypeUtil.TYPE_INTEGRATION:
            return self.go_integration()
        elif self.resource["type"] == TypeUtil.TYPE_WORKSPACE:
            return self.go_workspace()
        else:
            return 1

    def go_collection(self):
        workspace, collection_name = parse_collection_path(self.resource['name'])
        r = self.client.retrieve(name=collection_name, workspace=workspace)
        r.drop()
        self.lprint(
            0, '{} "{}" in workspace "{}" was dropped successfully.'.format(
                r.type.capitalize(), collection_name, workspace
            )
        )
        return 0

    def go_integration(self):
        i = self.client.Integration.drop(name=self.resource['name'])
        self.lprint(
            0, '{} "{}" was dropped successfully.'.format(
            TypeUtil.TYPE_INTEGRATION.capitalize(), i.get('name', '')
            )
        )
        return 0

    def go_workspace(self):
        w = self.client.Workspace.retrieve(name=self.resource['name'])
        w.drop()
        self.lprint(
            0, '{} "{}" was dropped successfully.'.format(
            TypeUtil.TYPE_WORKSPACE.capitalize(), w.name
            )
        )
        return 0

