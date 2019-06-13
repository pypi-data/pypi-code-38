import logging
import os
import configparser
import odoo

class CliBase(object):
    def __init__(self):
        self.config = None
        self._odoo_config = {}

    def load_config(self):
        config = configparser.ConfigParser()
        config.read([os.path.expanduser('~/.config/odoopti.cfg')])
        self.config = config

    def get_config(self, section, name):
        return self.config.get(section, name)

    def get_config_int(self, section, name):
        return self.config.getint(section, name)

    def get_config_bool(self, section, name):
        return self.config.getboolean(section, name)

    def configure_odoo(self, env_name):
        section = 'env:{}'.format(env_name)

        self._odoo_config['server_host'] = self.get_config(section, 'server_host')
        self._odoo_config['server_port'] = self.get_config_int(section, 'server_port')
        self._odoo_config['database'] = self.get_config(section, 'database')
        self._odoo_config['server_ssl'] = self.get_config_bool(section, 'server_ssl')

    def ext_cli_args(self, parser):
        pass

    def ext_cli_args_read(self, args):
        pass

    def parse_args(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--logging', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set log level', default='WARNING')
        parser.add_argument('-e', '--env', type=str, default='devel', help='Set environment')
        parser.add_argument('-u', '--user', type=str, default=os.environ['USER'], help='Set user name')
        self.ext_cli_args(parser)

        args = parser.parse_args()
        if args.logging:
            lvl = getattr(logging, args.logging, None)
            if isinstance(lvl, int):
                logging.getLogger().setLevel(lvl)

        self.ext_cli_args_read(args)

        self.configure_odoo(args.env)

    def bootstrap(self, args):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
        self.load_config()
