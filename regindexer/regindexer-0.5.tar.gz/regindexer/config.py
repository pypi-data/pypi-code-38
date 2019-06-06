import yaml

from regindexer.tag_pattern import TagPattern


class IndexConfig(object):
    def __init__(self, name, attrs):
        self.name = name
        self.output = attrs['output']
        self.registry = attrs['registry']
        self.registry_public = attrs.get('registry_public', self.registry)
        self.tags = [TagPattern(x) for x in attrs['tags']]
        self.required_annotations = attrs.get('required_annotations', [])
        self.architectures = attrs.get('architectures', None)
        self.extract_icons = attrs.get('extract_icons', False)

    def __repr__(self):
        return 'IndexConfig(%r)' % self.__dict__


class DaemonConfig(object):
    def __init__(self, attrs):
        self.topic_prefix = attrs.get('topic_prefix', 'org.fedoraproject')
        self.environment = attrs.get('environment', 'dev')


class Config(object):
    def __init__(self, path):
        self.indexes = []
        with open(path, 'r') as f:
            yml = yaml.safe_load(f)
            self.icons_dir = yml.get('icons_dir', None)
            self.icons_uri = yml.get('icons_uri', None)
            if not self.icons_uri.endswith('/'):
                self.icons_uri = self.icons_uri + '/'
            indexes = yml.get('indexes')
            if indexes:
                for name, attrs in indexes.items():
                    self.indexes.append(IndexConfig(name, attrs))

        self.daemon = DaemonConfig(yml.get('daemon', {}))
