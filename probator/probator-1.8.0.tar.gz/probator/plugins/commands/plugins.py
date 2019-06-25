from collections import namedtuple

from flask_script import Option
from more_itertools import first

from probator import PROBATOR_PLUGINS
from probator.constants import PLUGIN_NAMESPACES
from probator.plugins.commands import BaseCommand

ListPluginType = namedtuple('ListPluginType', ('cls', 'module'))


class ListPlugins(BaseCommand):
    """List the plugins currently installed on the system"""
    ns = 'command_plugins'
    name = 'ListPlugins'
    option_list = [
        Option('--type', type=str, default=None, metavar='TYPE', help='Only show plugins of this type',
               choices=list(PLUGIN_NAMESPACES.keys())
               )
    ]

    def run(self, **kwargs):
        self.log.info('--- List of Plugins ---')
        for ns, info in PROBATOR_PLUGINS.items():
            self.log.info(f'  {info.name.capitalize()} Plugins:')

            for entry_point in info['plugins']:
                self.log.info(f'    {first(entry_point.attrs)} from {entry_point.module_name}')

            self.log.info('')
        self.log.info('--- End list of Plugins ---')
