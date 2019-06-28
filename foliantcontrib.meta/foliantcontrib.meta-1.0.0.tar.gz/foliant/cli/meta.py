'''Main CLI responsible for the ``meta`` command.'''
from pathlib import Path
from pkgutil import iter_modules
from importlib import import_module

from cliar import set_help, set_arg_map, set_metavars

from foliant.cli.base import BaseCli
from foliant.config import Parser


class MetaCommandError(Exception):
    pass


def get_available_meta_commands() -> list:
    '''Get the names of installed ``foliant.meta_commands`` submodules.

    Used in the interactive meta command selection prompt to list the available
    meta commands.

    :returns: List of submodule names

    '''

    meta_commands_module = import_module('foliant.meta_commands')
    result = []
    for importer, modname, _ in iter_modules(meta_commands_module.__path__):
        if modname == 'base':
            continue
        result.append(modname)
    return result


class Cli(BaseCli):
    @staticmethod
    def validate_meta_command(meta_command: str) -> bool:
        '''Check that the specified meta command exists'''

        available_meta_commands = get_available_meta_commands()

        if meta_command not in available_meta_commands:
            raise MetaCommandError(
                f'Meta command {meta_command} not found. ' +
                f'Available commands are {", ".join(available_meta_commands)}.'
            )

        return True

    @set_arg_map({'project_path': 'path', 'config_file_name': 'config', 'meta_command': 'cmd'})
    @set_metavars({'meta_command': 'COMMAND', 'config_file_name': 'PATH'})
    @set_help(
        {
            'meta_command': 'Meta command to run',
            'project_path': 'Path to the directory with the config file (default: ".").',
            'config_file_name': 'Name of the Foliant config file (default: "foliant.yml").',
        }
    )
    def meta(self,
             meta_command,
             config_file_name='foliant.yml',
             project_path=Path('.')):
        '''Run meta command'''

        self.logger.info('Meta command started.')
        try:
            self.validate_meta_command(meta_command)
            config = Parser(project_path, config_file_name, self.logger).parse()
        except MetaCommandError as exception:
            self.logger.critical(str(exception))
            exit(str(exception))
        context = {
            'project_path': Path(project_path),
            'config': config,
        }
        meta_command_module = import_module(f'foliant.meta_commands.{meta_command}')
        self.logger.debug(f'Imported meta command {meta_command_module}.')

        meta_command_module.MetaCommand(context, self.logger).run()
        self.logger.info('Meta command finished.')
