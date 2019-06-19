import os, sys

import click

cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          'commands'))

class DongCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('dong.commands.cmd_' + name,
                             None, None, ['command'])
        except ImportError:
            return
        return mod.command


@click.command(cls=DongCLI)
def main():
    """Universal Command Line Interface for Libgirl AI Platform"""
    pass
