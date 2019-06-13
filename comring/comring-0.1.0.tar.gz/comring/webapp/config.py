import yaml
import collections

from . import utils

CONF = {}

def update_from_file(filename):
    cfg = None
    with open(filename, 'r') as cffile:
        cfg = yaml.load(cffile)
    if cfg:
        utils.dict_merge(CONF, cfg)
    return True
