import yaml


def dump(data, canonical=True, **kwds):
    return yaml.safe_dump(data, canonical=canonical, **kwds)


def load(s):
    return yaml.safe_load(s)
