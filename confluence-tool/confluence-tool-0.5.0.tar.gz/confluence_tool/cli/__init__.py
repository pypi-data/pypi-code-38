from os.path import expanduser
from confluence_tool import ConfluenceError, ConfluenceAPI
import pyaml, yaml
import logging
from yaml import SafeLoader

logging.basicConfig()

import keyring

class ConfigFileMissing(StandardError):
    pass

class Config:
    def __init__(self, **args):
        self.args = args

    def __getattr__(self, name):
        if name == 'config':
            self.config = self.readConfig()
            return self.config

        if name == 'config_file':
            if self.args.get('config_file'):
                self.config_file = self.args['config_file']
            else:
                self.config_file = expanduser('~/.confluence-tool.yaml')

            return self.config_file

        if name == 'confluence_api':
            self.confluence_api = self.getConfluenceAPI()
            return self.confluence_api

        return self.get(name)

    def dict(self, *args):
        result = {}
        for k in args:
            result[k] = self.get(k)
        return result

    def __getitem__(self, name):
        return self.args[name]

    def __setitem__(self, name, value):
        self.args[name] = value

    def __contains__(self, name):
        return name in self.args

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def readConfig(self):
        try:
            with open(self.config_file, 'r') as f:
                return yaml.load(f, Loader=SafeLoader)
        except Exception as e:
            if self.args.get('debug'):
                import traceback
                traceback.print_exc()

            raise ConfigFileMissing()

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

        if result['username'] and not result['password']:
            baseurl = result['baseurl']
            password = keyring.get_password('confluence-tool '+baseurl, result['username'])
            result['password'] = password

        return result

    def setConfig(self, update_password=False):
        config_name = self.args.get('config', 'default')

        try:
            config = self.config or {}
        except ConfigFileMissing:
            config = {}

        if 'default' not in config:
            config['default'] = {}

        old_baseurl = config[config_name].get('baseurl')
        old_username = config[config_name].get('username')

        print "ou: %s" % old_username

        baseurl  = self.args.get('baseurl')
        username = self.args.get('username')

        if baseurl is None:
            baseurl = old_baseurl
        if username is None:
            username = old_username

        if config_name in config:
            old_baseurl = config[config_name].get('baseurl')
            old_username = config[config_name].get('username')
            if old_baseurl != baseurl or old_username != username:
                try:
                    keyring.delete_password("confluence-tool "+old_baseurl, old_username)
                except:
                    pass

        config[config_name] = cfg = dict(
            baseurl  = baseurl,
            username = username,
        )

        print "Password will be stored in your systems keyring."
        import getpass
        password = getpass.getpass("Password (%s): " % username)
        keyring.set_password('confluence-tool '+baseurl, username, password)

        for k,v in cfg.items():
            if v is None:
                del cfg[k]

        self.config = config

        self.writeConfig()

    def rmConfig(self):
        config_name = self.args.get('config', 'default')

        try:
            config = self.config or {}
        except ConfigFileMissing:
            config = {}

        if config_name not in config:
            return

        keyring.delete_password('confluence-tool '+baseurl, username)

        del config[config_name]
        self.writeConfig()


    def getConfluenceAPI(self):
        return ConfluenceAPI(self.getConfig())

from .cli import command, arg

confluence_tool_config = {}


def main(argv=None):

    def config_factory(args, **kwargs):
        global confluence_tool_config
        confluence_tool_config = Config(**vars(args))
        if args.debug:
            log = logging.getLogger()
            log.setLevel(logging.DEBUG)

        return [confluence_tool_config], {}

    try:
        return command.execute(argv, compile=config_factory)

    except ConfigFileMissing as e:
        if confluence_tool_config.get('debug'):
            import traceback
            traceback.print_exc()
            return 1

        #print "Config file missing.  Please run 'confluence-tool config' or specify --baseurl"
        return 1

    except StandardError as e:
        if confluence_tool_config.get('debug'):
            import traceback
            traceback.print_exc()
            return 1
        else:
            print (u"%s" % e).encode('utf-8')
            return 1

import edit
import page_prop
import show
import config
import labels
import comala_workflow
import space

argparser = command.argparser
