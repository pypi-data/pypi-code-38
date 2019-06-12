import inspect
import configparser
from gt.sources.ssh import SSH
from gt.sources.gitlab import Gitlab
from gt.sources.github import GitHub

source_classes = {
        'github': GitHub,
        'gitlab': Gitlab,
        'ssh': SSH,
}

def get_sources(config_file):
    sources = {}
    cfg = configparser.ConfigParser()
    cfg.read(config_file)

    for section in cfg.sections():
        items = dict(cfg.items(section))
        if 'type' not in items:
            raise Exception('Git source \'%s\' missing type field.' % section)
        if items['type'] not in source_classes:
            raise Exception('Section \'%s\' has unrecognized source type \'%s\'' % (section, items['type']))

        target_cls = source_classes[items['type']]
        cls_params = inspect.getargspec(target_cls.__init__)[0][1:]
        items.pop('type')

        for param in cls_params:
            if param not in items:
                raise Exception('Git source \'%s\' requires parameter \'%s\'.' % (section, param))

        
        source = target_cls(**items)
        source.name = section
        sources[source.name] = source

    return sources
