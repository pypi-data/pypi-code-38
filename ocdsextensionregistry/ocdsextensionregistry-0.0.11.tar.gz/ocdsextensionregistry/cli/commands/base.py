from collections import defaultdict

from ocdsextensionregistry import ExtensionRegistry

from ocdsextensionregistry.exceptions import CommandError


class BaseCommand:
    def __init__(self, subparsers):
        """
        Initializes the subparser and adds arguments.
        """
        self.subparser = subparsers.add_parser(self.name, description=self.help)
        self.add_arguments()

    def add_arguments(self):
        pass

    def add_argument(self, *args, **kwargs):
        """
        Adds an argument to the subparser.
        """
        self.subparser.add_argument(*args, **kwargs)

    def handle(self):
        raise NotImplementedError('commands must implement handle()')

    def versions(self):
        registry = ExtensionRegistry(self.args.extension_versions_url, self.args.extensions_url)

        versions = defaultdict(list)
        for value in self.args.versions:
            if '==' in value:
                extension, version = value.split('==', 1)
                versions[extension].append(version)
            elif '=' in value:
                # Help users with a common error.
                raise CommandError("Couldn't parse '{}'. Use '==' not '='.".format(value))
            else:
                versions[value]

        for version in registry:
            if (not self.args.versions or version.id in versions) and (not versions[version.id] or version.version in versions[version.id]):  # noqa
                yield version
