'''
usage:
  bf props [options] <item> get [<key>]
  bf props [options] <item> set <key> <value> [--type=<type>]
  bf props [options] <item> rm  <key>

property options:
  -c --category=<cat>      Category of property [default: blackfynn]
  -t --type=<type>         Data type; string, integer, double, boolean, date, user [default: string]

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

from docopt import docopt

from blackfynn.models import Property

from .cli_utils import get_item


def get_prop(item, key, cat):
    prop = item.get_property(key, category=cat)
    if prop is None:
        print("Error: property key \'{k}\' not found (category={c})".format(k=key,c=cat))
        return
    return prop

def main(bf):
    args = docopt(__doc__)

    item = get_item(args['<item>'], bf)
    key  = args['<key>']
    cat  = args['--category']

    if args['get']:
        if key:
            prop = get_prop(item, key, cat)
            if prop is None: return
            print("{cat} / {key}: {value}".format(cat=prop.category, key=prop.key, value=prop.value))
            return
        for prop in item.properties:
            print(" * {cat} / {key}: {value}".format(cat=prop.category, key=prop.key, value=prop.value))
    elif args['set']:
        val  = args['<value>']
        dtype = args['--type']
        if dtype not in Property._data_types:
            print("Error: Data type must be one of {}".format(Property._data_types))
            return
        item.insert_property(key, val, category=cat, data_type=dtype)
        print("SET {cat} / {key} = {value} ({type})".format(cat=cat, key=key, value=val, type=dtype))
    elif args['rm']:
        prop = get_prop(item, key, cat)
        if prop is None: return
        item.remove_property(prop.key, category=prop.category)
        print("REMOVED {cat} / {key}".format(cat=cat, key=key))
