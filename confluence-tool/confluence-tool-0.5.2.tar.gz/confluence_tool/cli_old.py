"""
Confluence Commandline Interface

test

x

y

"""

import pyaml, yaml, sys, json, logging
import argparse
from os.path import expanduser
from confluence_tool import ConfluenceError, ConfluenceAPI
from textwrap import dedent
import difflib

def have_data_on_stdin():
    import sys
    import select

    if select.select([sys.stdin,],[],[],0.0)[0]:
        print "Have data!"
    else:
        print "No data"

from pprint import pprint

logging.basicConfig()

OUTPUT_FORMAT = 'yaml'

class Config:
    def __init__(self, **args):
        self.args = args

    def __getattr__(self, name):
        if name == 'config':
            self.config = self.readConfig()
            return self.config

        if name == 'config_file':
            if self.args['config_file']:
                self.config_file = self.args['config_file']
            else:
                self.config_file = expanduser('~/.confluence-tool.yaml')

            return self.config_file

        if name == 'confluence_api':
            self.confluence_api = self.getConfluenceAPI()
            return self.confluence_api

        try:
            return self[name]
        except KeyError:
            pass

        raise AttributeError(name)


    def dict(self, *args):
        result = {}
        for k in args:
            result[k] = self[k]
        return result

    def __getitem__(self, name):
        return self.args[name]

    def readConfig(self):
        with open(self.config_file, 'r') as f:
            return yaml.load(f)

    def writeConfig(self):
        with open(self.config_file, 'w') as f:
            pyaml.p(self.config, file=f)

    def getConfig(self):
        result = {}

        result.update(
            baseurl  = self.args.get('baseurl'),
            username = self.args.get('username'),
            password = self.args.get('password'),
            )

        if not result['baseurl'] or self.args.get('config'):
            config_name = self.args.get('config', 'default') or 'default'
            result.update(**self.config[config_name])

        return result

    def setConfig(self):
        config_name = self.args.get('config', 'default')
        self.config[config_name] = dict(
            baseurl  = self.args.get('baseurl'),
            username = self.args.get('username'),
            password = self.args.get('password'),
        )
        self.writeConfig()

    def getConfluenceAPI(self):
        return ConfluenceAPI(self.getConfig())



def dump(obj):
    if OUTPUT_FORMAT == 'yaml':
        try:
            pyaml.p(obj)
            return
        except ImportError:
            pass

    json.dump(obj, sys.stdout, indent=2)



def main(argv):
    args = argparser.parse_args(argv)
    opts = vars(args).copy()
    del opts['action']

    global OUTPUT_FORMAT
    if 'json' in opts:
        if opts['json']:
            OUTPUT_FORMAT = 'json'
        del opts['json']

    config = Config(**opts)
    try:
        args.action(config)
    except ConfluenceError as e:
        dump(json.loads(str(e)))
    except Exception as e:
        if config.debug:
            import traceback
            traceback.print_exc()
        else:
            sys.stderr.write("%s\n" % e)

        return 1


if __name__ == '__main__':

    sys.exit(main(sys.argv[1:]) or 0)
