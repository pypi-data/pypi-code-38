#!/usr/bin/env python

import click
import os, stat
from sys import path, exit
import sys
from os.path import expanduser
from signal import signal, SIGINT, getsignal
from datetime import datetime
import getpass
import json

__author__ = 'DataKitchen, Inc.'

home = expanduser('~')  # does not end in a '/'
if os.path.join(home, 'dev/DKCloudCommand') not in path:
    path.insert(0, os.path.join(home, 'dev/DKCloudCommand'))
from DKCloudCommand.modules.DKCloudAPI import DKCloudAPI
from DKCloudCommand.modules.DKCloudCommandConfig import DKCloudCommandConfig
from DKCloudCommand.modules.DKCloudCommandRunner import DKCloudCommandRunner
from DKCloudCommand.modules.DKKitchenDisk import DKKitchenDisk
from DKCloudCommand.modules.DKRecipeDisk import DKRecipeDisk
from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from DKCloudCommand.modules.DKCLIRecipeChecker import DKCLIRecipeChecker

DEFAULT_IP = 'https://cloud.datakitchen.io'
DEFAULT_PORT = '443'
DEFAULT_CONTEXT = 'default'

DK_VERSION = '1.0.124'

alias_exceptions = {'recipe-copy': 'ry',
                    'recipe-conflicts': 'rf',
                    'kitchen-config': 'kf',
                    'recipe-create': 're',
                    'file-diff': 'fdi',
                    'context-list': 'xl'}


class Backend(object):
    _short_commands = {}

    def __init__(self, only_check_version=False, current_command=None):
        self.cfg = None
        self.dki = None

        self.init_folders()

        if not self.check_version(self.cfg):
            exit(1)

        if only_check_version:
            return

        self.init_context()

        self.cfg.check_working_path()
        self.cfg.print_current_context(current_command)

    def init_folders(self):
        dk_temp_folder = os.path.join(home, '.dk')

        # Create path if do not exist
        try:
            os.makedirs(dk_temp_folder)
        except:
            pass
        cfg = DKCloudCommandConfig()
        cfg.set_dk_temp_folder(dk_temp_folder)
        self.cfg = cfg

    def init_context(self):
        # Check context
        dk_context_path = os.path.join(self.cfg.get_dk_temp_folder(), '.context')
        if not os.path.isfile(dk_context_path):
            DKFileHelper.write_file(dk_context_path, DEFAULT_CONTEXT)
        dk_context = DKFileHelper.read_file(dk_context_path)
        dk_customer_temp_folder = os.path.join(self.cfg.get_dk_temp_folder(), dk_context.strip())

        # Create path if do not exist
        try:
            os.makedirs(dk_customer_temp_folder)
        except:
            pass

        self.cfg.set_dk_customer_temp_folder(dk_customer_temp_folder)
        self.cfg.set_context(dk_context.strip())

        if not os.path.isfile(self.cfg.get_config_file_location()):
            perform_general_config = not os.path.isfile(self.cfg.get_general_config_file_location())
            self.setup_cli(self.cfg.get_config_file_location(), perform_general_config, True)

        if not self.cfg.init_from_file(self.cfg.get_config_file_location()):
            s = "Unable to load configuration from '%s'" % self.cfg.get_config_file_location()
            raise click.ClickException(s)
        self.dki = DKCloudAPI(self.cfg)
        if self.dki is None:
            s = 'Unable to create and/or connect to backend object.'
            raise click.ClickException(s)

        token = self.dki.login()

        if token is None:
            message = '\nLogin failed. You are in context %s, do you want to reconfigure your context? [yes/No]' % dk_context
            confirm = raw_input(message)
            if confirm.lower() != 'yes':
                exit(0)
            else:
                self.setup_cli(self.cfg.get_config_file_location(), False, True)
                print 'Context %s has been reconfigured' % dk_context
                exit(0)

    def check_version(self, cfg):
        if self.cfg.is_skip_version_check_present():
            return True

        if 'rc' in DK_VERSION:
            return True

        # Get current code version
        current_version = self.version_to_int(DK_VERSION)

        # Get latest version from local file
        latest_version_file = os.path.join(cfg.get_dk_temp_folder(), '.latest_version')
        latest_version = None
        if os.path.exists(latest_version_file):
            with open(latest_version_file,'r') as f:
                latest_version = f.read().strip()

        # Get latest version number from pypi API and update local file.
        try:
            latest_version = cfg.get_latest_version_from_pip()
        except:
            message = "Warning: could not get DKCloudCommand latest version number from pip."
            click.secho(message, fg='red')

        # update local file with latest version number from pip
        try:
            if latest_version is not None:
                with open(latest_version_file, 'w') as f:
                    f.write(latest_version)
        except:
            message = "Warning: %s file could not be written." % latest_version_file
            click.secho(message, fg='red')

        # If we are not in latest known version. Prompt the user to update.
        if latest_version and self.version_to_int(latest_version) > current_version:
            print '\033[31m***********************************************************************************\033[39m'
            print '\033[31m Warning !!!\033[39m'
            print '\033[31m Your command line is out of date, new version %s is available. Please update.\033[39m' % latest_version
            print ''
            print '\033[31m Type "pip install DKCloudCommand --upgrade" to upgrade.\033[39m'
            print '\033[31m***********************************************************************************\033[39m'
            print ''
            return False

        return True

    def version_to_int(self, version_str):
        tokens = self.padded_version(version_str).split('.')
        tokens.reverse()
        return sum([int(v) * pow(100,i) for i,v in enumerate(tokens)])

    def padded_version(self, version_str):
        while True:
            tokens = version_str.split('.')
            if len(tokens) >= 4:
                return version_str
            version_str += '.0'

    def setup_cli(self, file_path, general=False, context=False):
        if context:
            print ''
            username = raw_input('Enter username:')
            password = getpass.getpass('Enter password:')
            ip = raw_input('DK Cloud Address (default https://cloud.datakitchen.io):')
            port = raw_input('DK Cloud Port (default 443):')

            if not ip:
                ip = DEFAULT_IP
            if not port:
                port = DEFAULT_PORT

            print ''
            if username == '' or password == '':
                raise click.ClickException("Invalid credentials")

            data = {
                'dk-cloud-ip': ip,
                'dk-cloud-port': port,
                'dk-cloud-username': username,
                'dk-cloud-password': password
            }

            self.cfg.delete_jwt_from_file()

            with open(file_path, 'w+') as f:
                json.dump(data, f, indent=4)

        if general:
            merge_tool = raw_input('DK Cloud Merge Tool Template (default None):')
            diff_tool = raw_input('DK Cloud File Diff Tool Template (default None):')

            check_working_path = raw_input('Check current working path against existing contexts?[yes/No] (default No):')
            if check_working_path is not None and check_working_path.lower() == 'yes':
                check_working_path = True
            else:
                check_working_path = False

            hide_context_legend = raw_input('Hide current context legend on each command response?[yes/No] (default No):')
            if hide_context_legend is not None and hide_context_legend.lower() == 'yes':
                hide_context_legend = True
            else:
                hide_context_legend = False

            skip_recipe_checker = raw_input('Skip checking the recipe locally, before recipe-update like commands?[yes/No] (default No):')
            if skip_recipe_checker is not None and skip_recipe_checker.lower() == 'yes':
                skip_recipe_checker = True
            else:
                skip_recipe_checker = False

            self.cfg.configure_general_file(merge_tool, diff_tool, check_working_path, hide_context_legend, skip_recipe_checker)
        print '\n'

    @staticmethod
    def get_kitchen_name_soft(given_kitchen=None):
        """
        Get the kitchen name if it is available.
        :return: kitchen name or None
        """
        if given_kitchen is not None:
            return given_kitchen
        else:
            in_kitchen = DKCloudCommandRunner.which_kitchen_name()
            return in_kitchen

    @staticmethod
    def check_in_kitchen_root_folder_and_get_name():
        """
        Ensures that the caller is in a kitchen folder.
        :return: kitchen name or None
        """
        in_kitchen = DKCloudCommandRunner.which_kitchen_name()
        if in_kitchen is None:
            raise click.ClickException("Please change directory to a kitchen folder.")
        else:
            return in_kitchen

    @staticmethod
    def get_kitchen_from_user(kitchen=None):
        in_kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None and in_kitchen is None:
            raise click.ClickException("You must provide a kitchen name or be in a kitchen folder.")

        if in_kitchen is not None:
            use_kitchen = in_kitchen

        if kitchen is not None:
            use_kitchen = kitchen

        use_kitchen = Backend.remove_slashes(use_kitchen)

        return "ok", use_kitchen

    @staticmethod
    def get_recipe_name(recipe):
        in_recipe = DKRecipeDisk.find_recipe_name()
        if recipe is None and in_recipe is None:
            raise click.ClickException("You must provide a recipe name or be in a recipe folder.")
        elif recipe is not None and in_recipe is not None:
            raise click.ClickException(
                    "Please provide a recipe parameter or change directory to a recipe folder, not both.\nYou are in Recipe '%s'" % in_recipe)

        if in_recipe is not None:
            use_recipe = in_recipe
        else:
            use_recipe = recipe

        use_recipe = Backend.remove_slashes(use_recipe)
        return "ok", use_recipe

    @staticmethod
    def remove_slashes(name):
        if len(name) > 1 and (name.endswith('\\') or name.endswith('/')):
            return name[:-1]
        return name

    def set_short_commands(self, commands):
        short_commands = {}
        for long_command in commands:
            if long_command in alias_exceptions:
                short_commands[long_command] = alias_exceptions[long_command]
                continue
            parts = long_command.split('-')
            short_command = ''
            for part in parts:
                if part == 'orderrun':
                    short_command += 'or'
                else:
                    short_command += part[0]
            short_commands[long_command] = short_command
        self._short_commands = short_commands
        return self._short_commands

    def get_short_commands(self):
        return self._short_commands


def check_and_print(rc):
    if rc.ok():
        click.echo(rc.get_message())
    else:
        raise click.ClickException(rc.get_message())


class AliasedGroup(click.Group):

    def get_command(self, ctx, cmd_name):
        self._check_unique(ctx)
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        found_command = next(
            (long_command for long_command, short_command in alias_exceptions.items() if short_command == cmd_name),
            None)

        if found_command is not None:
            return click.Group.get_command(self, ctx, found_command)

        all_commands = self.list_commands(ctx)
        for long_command in all_commands:
            short_command = self.short_command(long_command)
            if short_command == cmd_name:
                return click.Group.get_command(self, ctx, long_command)
        ctx.fail("Unable to find command for alias '%s'" % cmd_name)

    def short_command(self,long_command):
        if long_command in alias_exceptions:
            return alias_exceptions[long_command]
        parts = long_command.split('-')
        short_command = ''
        for part in parts:
            if part == 'orderrun':
                short_command += 'or'
            else:
                short_command += part[0]
        return short_command

    def _check_unique(self, ctx):
        all_commands = self.list_commands(ctx)
        short_commands = {}
        for long_command in all_commands:
            if long_command in alias_exceptions:
                continue

            short_command = self.short_command(long_command)

            if short_command in short_commands:
                click.secho("The short alias %s is not ambiguous" % short_command, fg='red')
            else:
                short_commands[short_command] = long_command

    def format_commands(self, ctx, formatter):
        # override default behavior
        rows = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue

            help = cmd.short_help or ''
            rows.append(('%s (%s)' % (subcommand, self.short_command(subcommand)), help))

        if rows:
            with formatter.section('Commands'):
                formatter.write_dl(rows)


@click.group(cls=AliasedGroup)
@click.version_option(version=DK_VERSION)
@click.pass_context
def dk(ctx):
    ctx.obj = Backend(current_command=ctx.invoked_subcommand)
    ctx.obj.set_short_commands(ctx.command.commands)


# Use this to override the automated help
class DKClickCommand(click.Command):
    def __init__(self, name, context_settings=None, callback=None,
                 params=None, help=None, epilog=None, short_help=None,
                 options_metavar='[OPTIONS]', add_help_option=True):
        super(DKClickCommand, self).__init__(name, context_settings, callback,
                                             params, help, epilog, short_help,
                                             options_metavar, add_help_option)

    def get_help(self, ctx):
        # my_help = click.Command.get_help(ctx)
        my_help = super(DKClickCommand, self).get_help(ctx)
        return my_help


@dk.command(name='config-list', cls=DKClickCommand)
@click.pass_obj
def config_list(backend):
    """
    Print the current configuration.
    """
    try:
        click.secho('Current configuration is ...', fg='green')

        ret = str()
        customer_name = backend.dki.get_customer_name()
        if customer_name:
            ret += 'Customer Name:\t\t\t%s\n' % str(customer_name)
        ret += str(backend.dki.get_config())
        print ret
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='config',cls=DKClickCommand)
@click.option('--full', '-f', default=False, is_flag=True, required=False, help='General and context configuration')
@click.option('--context', '-c', default=False, is_flag=True, required=False, help='Context configuration')
@click.option('--general', '-g', default=False, is_flag=True, required=False, help='General configuration')
@click.pass_obj
def config(backend, full, context, general):
    """
    Configure Command Line.
    """
    try:
        if not any([full, context, general]):
            full = True
        if full:
            general = True
            context = True

        if context and backend.cfg.get_hide_context_legend():
            click.echo('Current context is: %s \n' % backend.cfg.get_current_context())

        backend.setup_cli(backend.cfg.get_config_file_location(), general, context)
        click.echo('Configuration changed!.\n')
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='context-list', cls=DKClickCommand)
@click.pass_obj
def context_list(backend):
    """
    List available contexts.

    """
    try:
        click.secho('Available contexts are ...\n')
        contexts = backend.cfg.context_list()
        for context in contexts:
            click.echo('%s' % context)
        if backend.cfg.get_hide_context_legend():
            click.echo('\nCurrent context is: %s \n' % backend.cfg.get_current_context())
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='context-delete', cls=DKClickCommand)
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.argument('context_name', required=True)
@click.pass_obj
def context_delete(backend, context_name, yes):
    """
    Deletes a context.

    """
    try:
        if not backend.cfg.context_exists(context_name):
            click.echo('\nContext does not exist.')
            return

        current_context = backend.cfg.get_current_context()
        if current_context == context_name:
            click.echo('Please switch to another context before proceeding')
            click.echo('Use context-switch command.')
            return

        if DEFAULT_CONTEXT == context_name:
            click.echo('Default context cannot be removed.')
            return

        if not yes:
            message = '\nCredential information will be lost.\n'
            message += 'Are you sure you want to delete context %s? [yes/No]' % context_name
            confirm = raw_input(message)
            if confirm.lower() != 'yes':
                click.echo('\nExiting.')
                return

        click.secho('Deleting context %s  ...\n' % context_name)
        backend.cfg.delete_context(context_name)
        click.secho('Done!')
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='context-switch', cls=DKClickCommand)
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.argument('context_name', required=True)
@click.pass_obj
def context_switch(backend, context_name, yes):
    """
    Create or switch to a new context.
    """
    try:
        context_name = context_name.strip()

        current_context = backend.cfg.get_current_context()
        if current_context == context_name:
            click.echo('You already are in context %s' % context_name)
            return

        if not backend.cfg.context_exists(context_name):
            if not yes:
                message = '\nContext does not exist. Are you sure you want to create context %s? [yes/No]' % context_name
                confirm = raw_input(message)
                if confirm.lower() != 'yes':
                    return
                backend.cfg.create_context(context_name)
        click.secho('Switching to context %s ...' % context_name)
        backend.cfg.switch_context(context_name)
        backend.init_context()
        click.echo('Context switch done.')
        click.echo('Use dk user-info and dk config-list to get context details.')
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='recipe-status')
@click.pass_obj
def recipe_status(backend):
    """
    Compare local recipe to remote recipe for the current recipe.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException('You are not in a Kitchen')
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException('You must be in a Recipe folder')
        recipe_name = DKRecipeDisk.find_recipe_name()
        click.secho("%s - Getting the status of Recipe '%s' in Kitchen '%s'\n\tversus directory '%s'" % (
            get_datetime(), recipe_name, kitchen, recipe_dir), fg='green')
        check_and_print(DKCloudCommandRunner.recipe_status(backend.dki, kitchen, recipe_name, recipe_dir))
    except Exception as e:
        error_message = e.message if e.message else str(e)
        raise click.ClickException(error_message)

# --------------------------------------------------------------------------------------------------------------------
# User and Authentication Commands
# --------------------------------------------------------------------------------------------------------------------
@dk.command(name='user-info')
@click.pass_obj
def user_info(backend):
    """
    Get information about this user.
    """
    try:
        check_and_print(DKCloudCommandRunner.user_info(backend.dki))
    except Exception as e:
        raise click.ClickException(str(e))


# --------------------------------------------------------------------------------------------------------------------
#  kitchen commands
# --------------------------------------------------------------------------------------------------------------------
def get_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@dk.command(name='kitchen-list')
@click.pass_obj
def kitchen_list(backend):
    """
    List all Kitchens
    """
    try:
        click.echo(click.style('%s - Getting the list of kitchens' % get_datetime(), fg='green'))
        check_and_print(DKCloudCommandRunner.list_kitchen(backend.dki))
    except Exception as e:
        raise click.ClickException(str(e))

@dk.command(name='kitchen-get')
@click.option('--recipe', '-r', type=str, multiple=True, help='Get the recipe along with the kitchen. Multiple allowed')
@click.option('--all','-a',is_flag=True,help='Get all recipes along with the kitchen.')
@click.argument('kitchen_name', required=True)
@click.pass_obj
def kitchen_get(backend, kitchen_name, recipe, all):
    """
    Get an existing Kitchen locally. You may also get one or multiple Recipes from the Kitchen.
    """
    try:
        found_kitchen = DKKitchenDisk.find_kitchen_name()
        if found_kitchen is not None and len(found_kitchen) > 0:
            raise click.ClickException("You cannot get a kitchen into an existing kitchen directory structure.")

        if len(recipe) > 0:
            click.secho("%s - Getting kitchen '%s' and the recipes %s" % (get_datetime(), kitchen_name, str(recipe)), fg='green')
        else:
            click.secho("%s - Getting kitchen '%s'" % (get_datetime(), kitchen_name), fg='green')

        check_and_print(DKCloudCommandRunner.get_kitchen(backend.dki, kitchen_name, os.getcwd(), recipe, all))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='kitchen-which')
@click.pass_obj
def kitchen_which(backend):
    """
    What Kitchen am I working in?
    """
    try:
        check_and_print(DKCloudCommandRunner.which_kitchen(backend.dki, None))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='kitchen-create')
@click.argument('kitchen', required=True)
@click.option('--parent', '-p', type=str, required=True, help='name of parent kitchen')
@click.option('--description', '-d', type=str, required=False, help='Kitchen description')
@click.pass_obj
def kitchen_create(backend, parent, description, kitchen):
    """
    Create and name a new child Kitchen. Provide parent Kitchen name.
    """
    try:
        if not DKCloudCommandRunner.kitchen_exists(backend.dki, parent):
            raise click.ClickException('Parent kitchen %s does not exist. Check spelling.' % parent)

        click.secho('%s - Creating kitchen %s from parent kitchen %s' % (get_datetime(), kitchen, parent), fg='green')
        master = 'master'
        if kitchen.lower() != master.lower():
            check_and_print(DKCloudCommandRunner.create_kitchen(backend.dki, parent, kitchen, description))
        else:
            raise click.ClickException('Cannot create a kitchen called %s' % master)
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='kitchen-delete')
@click.argument('kitchen', required=True)
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def kitchen_delete(backend, kitchen, yes):
    """
    Provide the name of the kitchen to delete
    """
    try:
        DKCloudCommandRunner.print_kitchen_children(backend.dki, kitchen)

        if not yes:
            confirm = raw_input('\nAre you sure you want to delete the remote copy of the Kitchen %s ? [yes/No]' % kitchen)
            if confirm.lower() != 'yes':
                return

        click.secho('%s - Deleting remote copy of kitchen %s. Local files will not change.' % (get_datetime(), kitchen), fg='green')
        master = 'master'
        if kitchen.lower() != master.lower():
            check_and_print(DKCloudCommandRunner.delete_kitchen(backend.dki, kitchen))
        else:
            raise click.ClickException('Cannot delete the kitchen called %s' % master)
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='kitchen-config')
@click.option('--kitchen', '-k', type=str, required=False, help='kitchen name')
@click.option('--add', '-a', type=str, required=False, nargs=2,
              help='Add a new override to this kitchen. This will update an existing override variable.\n'
                   'Usage: --add VARIABLE VALUE\n'
                   'Example: --add kitchen_override \'value1\'',
              multiple=True)
@click.option('--get', '-g', type=str, required=False, help='Get the value for an override variable.', multiple=True)
@click.option('--unset', '-u', type=str, required=False, help='Delete an override variable.', multiple=True)
@click.option('--listall', '-la', type=str, is_flag=True, required=False, help='List all variables and their values.')
@click.pass_obj
def kitchen_config(backend, kitchen, add, get, unset, listall):
    """
    Get and Set Kitchen variable overrides

    Example:
    dk kf -k Dev_Sprint -a kitchen_override 'value1'
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        check_and_print(DKCloudCommandRunner.config_kitchen(backend.dki, use_kitchen, add, get, unset, listall))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='kitchen-merge-preview')
@click.option('--source_kitchen', '-sk', type=str, required=False, help='source (from) kitchen name')
@click.option('--target_kitchen', '-tk', type=str, required=True, help='target (to) kitchen name')
@click.option('--clean_previous_run', '-cpr', default=False, is_flag=True, required=False, help='Clean previous run of this command')
@click.pass_obj
def kitchen_merge_preview(backend, source_kitchen, target_kitchen, clean_previous_run):
    """
    Preview the merge of two Kitchens. No change will actually be applied.
    Provide the names of the Source (Child) and Target (Parent) Kitchens.
    """

    try:
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is not None:
            message = 'Warning: You are inside a recipe. Please go at least one level above. This command is typically used from the level above kitchen level.'
            click.secho(message, fg='yellow')
            return

        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None and source_kitchen is None:
            raise click.ClickException('You are not in a Kitchen and did not specify a source_kitchen')

        if kitchen is not None and source_kitchen is not None and kitchen != source_kitchen:
            raise click.ClickException('There is a conflict between the kitchen in which you are, and the source_kitchen you have specified')

        if kitchen is not None:
            use_source_kitchen = kitchen
        else:
            use_source_kitchen = source_kitchen

        kitchens_root = DKKitchenDisk.find_kitchens_root(reference_kitchen_names=[use_source_kitchen, target_kitchen])
        if kitchens_root:
            DKCloudCommandRunner.check_local_recipes(backend.dki, kitchens_root, use_source_kitchen)
            DKCloudCommandRunner.check_local_recipes(backend.dki, kitchens_root, target_kitchen)
        else:
            click.secho('The root path for your kitchens was not found, skipping local checks.')

        click.secho('%s - Previewing merge Kitchen %s into Kitchen %s' % (get_datetime(), use_source_kitchen, target_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.kitchen_merge_preview(backend.dki, use_source_kitchen, target_kitchen, clean_previous_run))
    except Exception as e:
        error_message = e.message
        if 'Recipe' in e.message and 'does not exist on remote.' in e.message:
            error_message += ' Delete your local copy before proceeding.'
        raise click.ClickException(error_message)


@dk.command(name='kitchen-merge')
@click.option('--source_kitchen', '-sk', type=str, required=False, help='source (from) kitchen name')
@click.option('--target_kitchen', '-tk', type=str, required=True, help='target (to) kitchen name')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def kitchen_merge(backend, source_kitchen, target_kitchen, yes):
    """
    Merge two Kitchens. Provide the names of the Source (Child) and Target (Parent) Kitchens.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None and source_kitchen is None:
            raise click.ClickException('You are not in a Kitchen and did not specify a source_kitchen')

        if kitchen is not None and source_kitchen is not None and kitchen != source_kitchen:
            raise click.ClickException('There is a conflict between the kitchen in which you are, and the source_kitchen you have specified')

        if kitchen is not None:
            use_source_kitchen = kitchen
        else:
            use_source_kitchen = source_kitchen

        kitchens_root = DKKitchenDisk.find_kitchens_root(reference_kitchen_names=[use_source_kitchen, target_kitchen])
        if kitchens_root:
            DKCloudCommandRunner.check_local_recipes(backend.dki, kitchens_root, use_source_kitchen)
            DKCloudCommandRunner.check_local_recipes(backend.dki, kitchens_root, target_kitchen)
        else:
            click.secho('The root path for your kitchens was not found, skipping local checks.')

        if not yes:
            confirm = raw_input('Are you sure you want to merge the \033[1mremote copy of Source Kitchen %s\033[0m into the \033[1mremote copy of Target Kitchen %s\033[0m? [yes/No]'
                                % (use_source_kitchen, target_kitchen))
            if confirm.lower() != 'yes':
                return

        click.secho('%s - Merging Kitchen %s into Kitchen %s' % (get_datetime(), use_source_kitchen, target_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.kitchen_merge(backend.dki, use_source_kitchen, target_kitchen))

        retry = True
        while retry:
            try:
                DKCloudCommandRunner.update_local_recipes_with_remote(backend.dki, kitchens_root, target_kitchen)
                retry = False
            except Exception as e:
                confirm = raw_input('%s\nRetry? [yes/No]' % e.message)
                if confirm.lower() != 'yes':
                    retry = False

    except Exception as e:
        raise click.ClickException(str(e))


# --------------------------------------------------------------------------------------------------------------------
#  Recipe commands
# --------------------------------------------------------------------------------------------------------------------
@dk.command(name='recipe-list')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.pass_obj
def recipe_list(backend, kitchen):
    """
    List the Recipes in a Kitchen
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        click.secho("%s - Getting the list of Recipes for Kitchen '%s'" % (get_datetime(), use_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.list_recipe(backend.dki, use_kitchen))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='recipe-create')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--template', '-tm', type=str, help='template name')
@click.argument('name', required=True)
@click.pass_obj
def recipe_create(backend, kitchen, name, template):
    """
    Create a new Recipe.

    Available templates: qs1, qs2, qs3
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        click.secho("%s - Creating Recipe %s for Kitchen '%s'" % (get_datetime(), name, use_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.recipe_create(backend.dki, use_kitchen, name, template=template))
    except Exception as e:
        raise click.ClickException(str(e))

@dk.command(name='recipe-copy')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.argument('source', required=True)
@click.argument('name', required=True)
@click.pass_obj
def recipe_copy(backend, kitchen, source, name):
    """
    Create a new Recipe based on the given recipe.

    Example:
    dk ry -k my_kitchen existing_recipe my_brand_new_recipe

    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        click.secho("%s - Creating Recipe %s from recipe %s for Kitchen '%s'" % (get_datetime(), name, source, use_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.recipe_copy(backend.dki, use_kitchen, source, name))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='recipe-delete')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.argument('name', required=True)
@click.pass_obj
def recipe_delete(backend,kitchen,name, yes):
    """
    Deletes local and remote copy of the given recipe
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)

        click.secho("This command will delete the local and remote copy of recipe '%s' for kitchen '%s'. " % (name, use_kitchen))
        if not yes:
            confirm = raw_input('Are you sure you want to delete the local and remote copy of recipe %s? [yes/No]' % name)
            if confirm.lower() != 'yes':
                return

        click.secho("%s - Deleting Recipe %s for Kitchen '%s'" % (get_datetime(), name, use_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.recipe_delete(backend.dki, use_kitchen,name))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='recipe-get')
@click.option('--delete_local', '-d', default=False, is_flag=True, required=False, help='Deletes Recipe files that only exist on local.')
@click.option('--overwrite', '-o', default=False, is_flag=True, required=False, help='Overwrites local version of Recipe files if said files exist on remote.')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help="Force through the command's subprompt.")
@click.argument('recipe', required=False)
@click.pass_obj
def recipe_get(backend, recipe, delete_local, overwrite, yes):
    """
    Get the latest remote versions of Recipe files. Changes will be auto-merged to local where possible.
    Conflicts will be written to local such that the impacted files contain full copies of both remote and local
    versions for the user to manually resolve. Local vs remote conflicts can be viewed via the file-diff
    command.

    """
    try:
        recipe_root_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_root_dir is None:
            if recipe is None:
                raise click.ClickException("\nPlease change to a recipe folder or provide a recipe name arguement")

            # raise click.ClickException('You must be in a Recipe folder')
            kitchen_root_dir = DKKitchenDisk.is_kitchen_root_dir()
            if not kitchen_root_dir:
                raise click.ClickException("\nPlease change to a recipe folder or a kitchen root dir.")
            recipe_name = recipe
            start_dir = DKKitchenDisk.find_kitchen_root_dir()
        else:
            recipe_name = DKRecipeDisk.find_recipe_name()
            if recipe is not None:
                if recipe_name != recipe:
                    raise click.ClickException("\nThe recipe name argument '%s' is inconsistent with the current directory '%s'" % (recipe, recipe_root_dir))
            start_dir = recipe_root_dir

        kitchen_name = Backend.get_kitchen_name_soft()
        click.secho("%s - Getting the latest version of Recipe '%s' in Kitchen '%s'" % (get_datetime(), recipe_name, kitchen_name), fg='green')
        check_and_print(DKCloudCommandRunner.get_recipe(backend.dki, kitchen_name, recipe_name, start_dir, delete_local=delete_local, overwrite=overwrite, yes=yes))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='recipe-compile')
@click.option('--variation', '-v', type=str, required=True, help='variation name')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--recipe', '-r', type=str, help='recipe name')
@click.pass_obj
def recipe_compile(backend, kitchen, recipe, variation):
    """
    Apply variables to a Recipe
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)

        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException('You must be in a recipe folder, or provide a recipe name.')

        click.secho('%s - Get the Compiled Recipe %s.%s in Kitchen %s' % (get_datetime(), recipe, variation, use_kitchen),
                    fg='green')
        check_and_print(DKCloudCommandRunner.get_compiled_order_run(backend.dki, use_kitchen, recipe, variation))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='file-compile')
@click.option('--variation', '-v', type=str, required=True, help='variation name')
@click.option('--file', '-f', type=str, required=True, help='file path')
@click.pass_obj
def file_compile(backend, variation, file):
    """
    Apply variables to a File
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException('You are not in a Kitchen')

        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException('You must be in a Recipe folder')
        recipe_name = DKRecipeDisk.find_recipe_name()

        click.secho('%s - Get the Compiled File of Recipe %s.%s in Kitchen %s' % (get_datetime(), recipe_name, variation, kitchen),
                    fg='green')
        check_and_print(DKCloudCommandRunner.get_compiled_file(backend.dki, kitchen, recipe_name, variation, file))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='file-history')
@click.option('--change_count', '-cc', type=int, required=False, default=0, help='Number of last changes to display')
@click.argument('filepath', required=True)
@click.pass_obj
def file_history(backend, change_count, filepath):
    """
    Show file change history.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException('You are not in a Kitchen')

        recipe = DKRecipeDisk.find_recipe_name()
        if recipe is None:
            raise click.ClickException('You must be in a recipe folder.')

        click.secho("%s - Retrieving file history" % get_datetime())

        if not os.path.exists(filepath):
            raise click.ClickException('%s does not exist' % filepath)
        check_and_print(DKCloudCommandRunner.file_history(backend.dki, kitchen,recipe,filepath,change_count))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='recipe-validate')
@click.option('--variation', '-v', type=str, required=True, help='variation name')
@click.pass_obj
def recipe_validate(backend, variation):
    """
    Validates local copy of a recipe, returning a list of errors and warnings. If there are no local changes, will only
    validate remote files.

    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException('You are not in a Kitchen')
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException('You must be in a Recipe folder')
        recipe_name = DKRecipeDisk.find_recipe_name()

        if not backend.cfg.get_skip_recipe_checker():
            click.secho('Performing local recipe check...',fg='green')
            DKCLIRecipeChecker(backend.cfg).check_recipe(recipe_dir)
            click.secho('Local recipe check done.')
        click.secho('%s - Validating recipe/variation %s.%s in Kitchen %s' % (get_datetime(), recipe_name, variation, kitchen),
                    fg='green')
        check_and_print(DKCloudCommandRunner.recipe_validate(backend.dki, kitchen, recipe_name, variation))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='recipe-variation-list')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--recipe', '-r', type=str, help='recipe name')
@click.pass_obj
def recipe_variation_list(backend, kitchen, recipe):
    """
    Shows the available variations for the current recipe in a kitchen
    """
    try:
        recipe_local = DKRecipeDisk.find_recipe_name()
        if recipe_local is None:
            get_remote = True
            err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
            if use_kitchen is None:
                raise click.ClickException(err_str)
            if recipe is None:
                raise click.ClickException('You must be in a recipe folder, or provide a recipe name.')
            use_recipe = Backend.remove_slashes(recipe)
            click.secho('Getting variations from remote ...', fg='green')
        else:
            get_remote = False
            use_recipe = recipe_local
            use_kitchen = DKCloudCommandRunner.which_kitchen_name()
            if use_kitchen is None:
                raise click.ClickException('You are not in a Kitchen')
            click.secho('Getting variations from local ...', fg='green')

        if not DKCloudCommandRunner.kitchen_exists(backend.dki, use_kitchen):
            raise click.ClickException('Kitchen %s does not exist. Check spelling.' % use_kitchen)

        click.secho('%s - Listing variations for recipe %s in Kitchen %s' % (get_datetime(), use_recipe, use_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.recipe_variation_list(backend.dki, use_kitchen, use_recipe, get_remote))
    except Exception as e:
        raise click.ClickException(str(e))

@dk.command(name='recipe-ingredient-list')
@click.pass_obj
def recipe_ingredient_list(backend):
    """
    Shows the available ingredients for the current recipe in a kitchen
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException('You are not in a Kitchen')
        print kitchen
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException('You must be in a Recipe folder')
        recipe_name = DKRecipeDisk.find_recipe_name()

        click.secho('%s - Listing ingredients for recipe %s in Kitchen %s' % (get_datetime(), recipe_name, kitchen),
                    fg='green')
        check_and_print(DKCloudCommandRunner.recipe_ingredient_list(backend.dki, kitchen, recipe_name))
    except Exception as e:
        raise click.ClickException(str(e))


# --------------------------------------------------------------------------------------------------------------------
#  File commands
# --------------------------------------------------------------------------------------------------------------------
@dk.command(name='file-diff')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--recipe', '-r', type=str, help='recipe name')
@click.argument('filepath', required=True)
@click.pass_obj
def file_diff(backend, kitchen, recipe, filepath):
    """
    Show differences with remote version of the file

    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException('You must be in a Recipe folder')
        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException('You must be in a recipe folder, or provide a recipe name.')

        click.secho('%s - File Diff for file %s, in Recipe (%s) in Kitchen (%s)' %
                    (get_datetime(), filepath, recipe, use_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.file_diff(backend.dki, use_kitchen, recipe, recipe_dir, filepath))
    except Exception as e:
        raise click.ClickException(str(e))

@dk.command(name='file-merge')
@click.option('--source_kitchen', '-sk', type=str, required=False, help='source (from) kitchen name')
@click.option('--target_kitchen', '-tk', type=str, required=True, help='target (to) kitchen name')
@click.argument('filepath', required=True)
@click.pass_obj
def file_merge(backend, source_kitchen, target_kitchen, filepath):
    """
    To be used after kitchen-merge-preview command.
    Launch the merge tool of choice, to resolve conflicts.
    File path needs to be stated as it is coming from kitchen-merge-preview output

    """
    try:
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is not None:
            message_1 = 'Warning: You are inside a recipe. Please go at least one level above. This command is typically used from the level above kitchen level.'
            message_2 = 'Keep in mind that the file path needs to be stated as it is coming from kitchen-merge-preview output.'
            message_3 = 'i.e. dk file-merge -sk source_kitchen_name -tk target_kitchen_name %s' % os.path.normpath('recipe_name/graph.json')
            click.secho(message_1, fg='yellow')
            click.secho(message_2, fg='yellow')
            click.secho(message_3, fg='yellow')
            return

        kitchen = DKCloudCommandRunner.which_kitchen_name()

        if kitchen is None and source_kitchen is None:
            raise click.ClickException('You are not in a Kitchen and did not specify a source_kitchen')

        if kitchen is not None and source_kitchen is not None and kitchen != source_kitchen:
            raise click.ClickException('There is a conflict between the kitchen in which you are, and the source_kitchen you have specified')

        if kitchen is not None:
            use_source_kitchen = kitchen
        else:
            use_source_kitchen = source_kitchen

        click.secho('%s - File Merge for file %s, source kitchen (%s), target kitchen(%s)' %
                    (get_datetime(), filepath, use_source_kitchen, target_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.file_merge(backend.dki, filepath, use_source_kitchen, target_kitchen))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='file-resolve')
@click.option('--source_kitchen', '-sk', type=str, required=False, help='source (from) kitchen name')
@click.option('--target_kitchen', '-tk', type=str, required=True, help='target (to) kitchen name')
@click.argument('filepath', required=True)
@click.pass_obj
def file_resolve(backend, source_kitchen, target_kitchen, filepath):
    """
    Mark a conflicted file as resolved, so that a merge can be completed
    File path needs to be stated as it is coming from kitchen-merge-preview output
    """
    try:
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is not None:
            message_1 = 'Warning: You are inside a recipe. Please go at least one level above. This command is typically used from the level above kitchen level.'
            message_2 = 'Keep in mind that the file path needs to be stated as it is coming from kitchen-merge-preview output.'
            message_3 = 'i.e. dk file-resolve -sk source_kitchen_name -tk target_kitchen_name %s' % os.path.normpath('recipe_name/graph.json')
            click.secho(message_1, fg='yellow')
            click.secho(message_2, fg='yellow')
            click.secho(message_3, fg='yellow')
            return

        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None and source_kitchen is None:
            raise click.ClickException('You are not in a Kitchen and did not specify a source_kitchen')

        if kitchen is not None and source_kitchen is not None and kitchen != source_kitchen:
            raise click.ClickException('There is a conflict between the kitchen in which you are, and the source_kitchen you have specified')

        if kitchen is not None:
            use_source_kitchen = kitchen
        else:
            use_source_kitchen = source_kitchen

        click.secho("%s - File resolve for file %s, source kitchen (%s), target kitchen(%s)" %
                    (get_datetime(), filepath, use_source_kitchen, target_kitchen))
        check_and_print(DKCloudCommandRunner.file_resolve(backend.dki, use_source_kitchen, target_kitchen, filepath))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='file-get')
@click.argument('filepath', required=True)
@click.pass_obj
def file_get(backend, filepath):
    """
    Get the latest version of a file from the server and overwriting your local copy.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException('You must be in a Kitchen')
        recipe = DKRecipeDisk.find_recipe_name()
        if recipe is None:
            raise click.ClickException('You must be in a recipe folder.')

        click.secho('%s - Getting File (%s) to Recipe (%s) in kitchen(%s)' %
                    (get_datetime(), filepath, recipe, kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.get_file(backend.dki, kitchen, recipe, filepath))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='file-update')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--recipe', '-r', type=str, help='recipe name')
@click.option('--message', '-m', type=str, required=True, help='change message')
@click.argument('filepath', required=True, nargs=-1)
@click.pass_obj
def file_update(backend, kitchen, recipe, message, filepath):
    """
    Update a Recipe file
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException('You must be in a Recipe folder')
        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException('You must be in a recipe folder, or provide a recipe name.')

        click.secho('%s - Updating File(s) (%s) in Recipe (%s) in Kitchen(%s) with message (%s)' %
                    (get_datetime(), filepath, recipe, use_kitchen, message), fg='green')
        check_and_print(DKCloudCommandRunner.update_file(backend.dki, use_kitchen, recipe, recipe_dir, message, filepath))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='recipe-update')
@click.option('--delete_remote', '-d', default=False, is_flag=True, required=False, help='Delete remote files to match local')
@click.option('--message', '-m', type=str, required=True, help='change message')
@click.pass_obj
def file_update_all(backend, message, delete_remote):
    """
    Update all of the changed files for this Recipe
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException('You must be in a Kitchen')
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException('You must be in a Recipe folder')
        recipe = DKRecipeDisk.find_recipe_name()

        click.secho('%s - Updating all changed files in Recipe (%s) in Kitchen(%s) with message (%s)' %
                    (get_datetime(), recipe, kitchen, message), fg='green')
        DKCLIRecipeChecker(backend.cfg).check_recipe(recipe_dir)
        check_and_print(DKCloudCommandRunner.update_all_files(backend.dki, kitchen, recipe, recipe_dir, message, delete_remote=delete_remote))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='file-delete')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--recipe', '-r', type=str, help='recipe name')
@click.option('--message', '-m', type=str, required=True, help='change message')
@click.argument('filepath', required=True, nargs=-1)
@click.pass_obj
def file_delete(backend, kitchen, recipe, message, filepath):
    """
    Delete one or more Recipe files. If you are not in a recipe path, provide the file path(s) relative to the recipe root.
    Separate multiple file paths with spaces.  File paths need no preceding backslash.

    To delete the directory, delete all files in that directory and then the directory will automatically be deleted.

    Example...

    dk file-delete -m "my delete message" file1.json dir2/file2.json
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException('You must be in a recipe folder, or provide a recipe name.')

        click.secho('%s - Deleting (%s) in Recipe (%s) in kitchen(%s) with message (%s)' %
                    (get_datetime(), filepath, recipe, use_kitchen, message), fg='green')
        check_and_print(DKCloudCommandRunner.delete_file(backend.dki, use_kitchen, recipe, message, filepath))
    except Exception as e:
        raise click.ClickException(str(e))


# --------------------------------------------------------------------------------------------------------------------
#  Active Serving commands
# --------------------------------------------------------------------------------------------------------------------

@dk.command(name='active-serving-watcher')
@click.option('--kitchen', '-k', type=str, required=False, help='Kitchen name')
@click.option('--interval', '-i', type=int, required=False, default=5, help='watching interval, in seconds')
@click.pass_obj
def active_serving_watcher(backend, kitchen, interval):
    """
    Watches all cooking Recipes in a Kitchen. Provide the Kitchen name as an argument or be in a Kitchen folder. Optionally provide a watching period as an integer, in seconds. Ctrl+C to terminate.
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        click.secho('%s - Watching Active OrderRun Changes in Kitchen %s' % (get_datetime(), use_kitchen), fg='green')
        DKCloudCommandRunner.watch_active_servings(backend.dki, use_kitchen, interval)
        while True:
            try:
                DKCloudCommandRunner.join_active_serving_watcher_thread_join()
                if not DKCloudCommandRunner.watcher_running():
                    break
            except KeyboardInterrupt:
                print 'KeyboardInterrupt'
                exit_gracefully(None, None)
        exit(0)
    except Exception as e:
        raise click.ClickException(str(e))


# --------------------------------------------------------------------------------------------------------------------
#  Order commands
# --------------------------------------------------------------------------------------------------------------------

@dk.command(name='order-run')
@click.argument('variation', required=True)
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--recipe', '-r', type=str, help='recipe name')
@click.option('--node', '-n', type=str, required=False, help='Name of the node to run')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.option('--params', '-p', required=False, help='Overrides passed as parameters')
@click.pass_obj
def order_run(backend, kitchen, recipe, variation, node, yes,params):
    """
    Run an order: cook a recipe variation

    Examples:

        \b
        1) run an order
        dk or -y -k myKitchen myVariation

        \b
        2) run an order with just one node
        dk or -y -k myKitchen -n myNode myVariation

        \b
        3) run an order with parameters (Linux version)
        dk or -y -k myKitchen -p '{"my-key":"my-value"}' myVariation

        \b
        4) run an order with parameters (Windows version)
        dk or -y -k myKitchen -p "{\\"my-key\\":\\"my-value\\"}" myVariation

    Note that:

        \b
        if a node is selected, as in example 2, variation's schedule will be overridden and the node will be executed immediately.

        \b
        In examples 3 and 4, variable 'my-key' will be added to running order, and will have highest precedence in case variable already exists in the recipe.
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException('You must be in a recipe folder, or provide a recipe name.')

        if not yes:
            confirm = raw_input('Kitchen %s, Recipe %s, Variation %s.\n'
                                'Are you sure you want to run an Order? [yes/No]'
                                % (use_kitchen, recipe, variation))
            if confirm.lower() != 'yes':
                return

        msg = '%s - Create an Order:\n\tKitchen: %s\n\tRecipe: %s\n\tVariation: %s\n' % (get_datetime(), use_kitchen, recipe, variation)
        if node is not None:
            msg += '\tNode: %s\n' % node

        click.secho(msg, fg='green')

        params_json = _parse_params(params)

        check_and_print(DKCloudCommandRunner.create_order(backend.dki, use_kitchen, recipe, variation, node, params_json))
    except Exception as e:
        raise click.ClickException(str(e))


def _parse_params(params):
    if params:
        if params[0] == '@':
            with open(params,'r') as f: return json.load(f)
        else:
            try:
                return json.loads(params)
            except:
                raise click.ClickException('Invalid parameters format, they must be a file reference or a well formatted JSON string')
                pass
    return None

@dk.command(name='order-delete')
@click.option('--kitchen', '-k', type=str, default=None, help='kitchen name')
@click.option('--order_id', '-o', type=str, default=None, help='Order ID')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def order_delete(backend, kitchen, order_id, yes):
    """
    Delete one order or all orders in a kitchen
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        print use_kitchen
        if use_kitchen is None:
            raise click.ClickException('You must specify either a kitchen or be in a kitchen directory')

        if not yes:
            if order_id is None:
                confirm = raw_input('Are you sure you want to delete all Orders in kitchen %s ? [yes/No]' % use_kitchen)
            else:
                confirm = raw_input('Are you sure you want to delete Order %s ? [yes/No]' % order_id)
            if confirm.lower() != 'yes':
                return

        if order_id is not None:
            click.secho('%s - Delete an Order using id %s' % (get_datetime(), order_id), fg='green')
            check_and_print(DKCloudCommandRunner.delete_one_order(backend.dki, use_kitchen, order_id))
        else:
            click.secho('%s - Delete all orders in Kitchen %s' % (get_datetime(), use_kitchen), fg='green')
            check_and_print(DKCloudCommandRunner.delete_all_order(backend.dki, use_kitchen))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='order-stop')
@click.option('--kitchen', '-k', type=str, default=None, help='kitchen name')
@click.option('--order_id', '-o', type=str, required=True, help='Order ID')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def order_stop(backend, order_id, kitchen, yes):
    """
    Stop an order - Turn off the serving generation ability of an order.  Stop any running jobs.  Keep all state around.
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException('You must specify either a kitchen or be in a kitchen directory')

        if order_id is None:
            raise click.ClickException('invalid order id %s' % order_id)

        if not yes:
            confirm = raw_input('Are you sure you want to stop Order %s? [yes/No]' % order_id)
            if confirm.lower() != 'yes':
                return

        click.secho('%s - Stop order id %s' % (get_datetime(), order_id), fg='green')
        check_and_print(DKCloudCommandRunner.stop_order(backend.dki, use_kitchen, order_id))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='orderrun-stop')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--order_run_id', '-ori', type=str, required=True, help='OrderRun ID')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def orderrun_stop(backend, kitchen, order_run_id, yes):
    """
    Stop the run of an order - Stop the running order and keep all state around.
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException('You must specify either a kitchen or be in a kitchen directory')

        if order_run_id is None:
            raise click.ClickException('invalid order id %s' % order_run_id)

        if not yes:
            confirm = raw_input('Are you sure you want to stop Order-Run %s ? [yes/No]' % order_run_id)
            if confirm.lower() != 'yes':
                return

        click.secho('%s - Stop order id %s' % (get_datetime(), order_run_id), fg='green')
        check_and_print(DKCloudCommandRunner.stop_orderrun(backend.dki, use_kitchen, order_run_id.strip()))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='orderrun-info')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--order_id', '-o', type=str, default=None, help='Order ID')
@click.option('--order_run_id', '-ori', type=str, default=None, help='OrderRun ID to display')
@click.option('--summary', '-s', default=False, is_flag=True, required=False, help='display run summary information')
@click.option('--nodestatus', '-ns', default=False, is_flag=True, required=False, help=' display node status info')
@click.option('--full_log', '-fl', default=False, is_flag=True, required=False, help='display full logs')
@click.option('--log', '-l', default=False, is_flag=True, required=False, help='display log info')
@click.option('--log_threshold', '-lt', type=str, default='INFO', required=False,
              help='Log display threshold. Can be ERROR, INFO, DEBUG, TRACE. Default value is INFO. This does not affect full_log')
@click.option('--timing', '-t', default=False, is_flag=True, required=False, help='display timing results')
@click.option('--test', '-q', default=False, is_flag=True, required=False, help='display test results')
@click.option('--runstatus', default=False, is_flag=True, required=False,
              help=' display status of the run (single line)')
@click.option('--disp_order_id', default=False, is_flag=True, required=False,
              help=' display the order id (single line)')
@click.option('--disp_orderrun_id', default=False, is_flag=True, required=False,
              help=' display order run id (single line)')
@click.option('--all_things', '-at', default=False, is_flag=True, required=False, help='display all information')
# @click.option('--recipe', '-r', type=str, help='recipe name')
@click.pass_obj
def orderrun_detail(backend, kitchen, summary, nodestatus, runstatus, full_log, log, log_threshold, timing, test, all_things,
                    order_id, order_run_id, disp_order_id, disp_orderrun_id):
    """
    Display information about an Order-Run
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        # if recipe is None:
        #     recipe = DKRecipeDisk.find_reciper_name()
        #     if recipe is None:
        #         raise click.ClickException('You must be in a recipe folder, or provide a recipe name.')
        pd = dict()
        if all_things:
            pd['summary'] = True
            pd['logs'] = True
            pd['timingresults'] = True
            pd['testresults'] = True
            # pd['state'] = True
            pd['status'] = True
        if summary:
            pd['summary'] = True
        if log:
            pd['logs'] = True
        if timing:
            pd['timingresults'] = True
        if test:
            pd['testresults'] = True
        if nodestatus:
            pd['status'] = True

        if runstatus:
            pd['runstatus'] = True
        if disp_order_id:
            pd['disp_order_id'] = True
        if disp_orderrun_id:
            pd['disp_orderrun_id'] = True

        # if the user does not specify anything to display, show the summary information
        if not runstatus and \
                not all_things and \
                not test and \
                not timing and \
                not log and \
                not nodestatus and \
                not summary and \
                not disp_order_id and \
                not disp_orderrun_id:
            pd['summary'] = True

        if order_id is not None and order_run_id is not None:
            raise click.ClickException("Cannot specify both the Order Id and the OrderRun Id")
        if order_id is not None:
            pd['serving_book_hid'] = order_id.strip()
        elif order_run_id is not None:
            pd['serving_hid'] = order_run_id.strip()

        log_threshold_options = {'ERROR', 'INFO', 'DEBUG', 'TRACE'}
        if log_threshold not in log_threshold_options:
            log_threshold_options_str = 'ERROR, INFO, DEBUG, TRACE'
            raise click.ClickException("log_threshold needs to be one of this options: %s" % log_threshold_options_str)

        # don't print the green thing if it is just runstatus
        if not runstatus and not disp_order_id and not disp_orderrun_id:
            backend.cfg.print_current_context()
            click.secho('%s - Display Order-Run details from kitchen %s' % (get_datetime(), use_kitchen), fg='green')
        check_and_print(DKCloudCommandRunner.orderrun_detail(backend.dki, use_kitchen, pd, full_log=full_log, log_threshold=log_threshold))
    except Exception as e:
        if not runstatus and not disp_order_id and not disp_orderrun_id:
            raise click.ClickException(str(e))
        else:
            click.echo('UNKNOWN')


@dk.command('orderrun-delete')
@click.argument('orderrun_id', required=True)
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.pass_obj
def delete_orderrun(backend, orderrun_id, kitchen, yes):
    """
    Delete the orderrun specified by the argument.
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException('You must specify either a kitchen or be in a kitchen directory')

        if orderrun_id is None:
            raise click.ClickException('invalid order id %s' % orderrun_id)

        if not yes:
            confirm = raw_input('Are you sure you want to delete Order-Run  %s ? [yes/No]' % orderrun_id)
            if confirm.lower() != 'yes':
                return

        click.secho('%s - Deleting orderrun %s' % (get_datetime(), orderrun_id), fg='green')
        check_and_print(DKCloudCommandRunner.delete_orderrun(backend.dki, use_kitchen, orderrun_id.strip()))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command('orderrun-resume')
@click.argument('orderrun_id', required=True)
@click.option('--kitchen', '-k', type=str, help='kitchen name')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def order_resume(backend, orderrun_id, kitchen, yes):
    """
    Resumes a failed order run
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException('You must specify either a kitchen or be in a kitchen directory')

        if orderrun_id is None:
            raise click.ClickException('invalid order id %s' % orderrun_id)

        if not yes:
            confirm = raw_input('Are you sure you want to resume Order-Run %s ? [yes/No]' % orderrun_id)
            if confirm.lower() != 'yes':
                return

        click.secho('%s - Resuming Order-Run %s' % (get_datetime(), orderrun_id), fg='green')
        check_and_print(DKCloudCommandRunner.order_resume(backend.dki, use_kitchen, orderrun_id.strip()))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='order-list')
@click.option('--kitchen', '-k', type=str, required=False, help='Filter results for kitchen only')
@click.option('--start', '-s', type=int, required=False, default=0, help='Start offset for displaying orders')
@click.option('--order_count', '-oc', type=int, required=False, default=5, help='Number of orders to display')
@click.option('--order_run_count', '-orc', type=int, required=False, default=3, help='Number of order runs to display, for each order')
@click.option('--recipe', '-r', type=str, required=False, default=None, help='Filter results for this recipe only')
@click.pass_obj
def order_list(backend, kitchen, order_count, order_run_count, start, recipe):
    """
    List Orders in a Kitchen.

    Examples:

    1) Basic usage with no paging, 5 orders, 3 order runs per order.

    dk order-list

    2) Get first, second and third page, ten orders per page, two order runs per order.

    dk order-list --start 0  --order_count 10 --order_run_count 2

    dk order-list --start 10 --order_count 10 --order_run_count 2

    dk order-list --start 20 --order_count 10 --order_run_count 2

    3) Get first five orders per page, two order runs per order, for recipe recipe_name

    dk order-list --recipe recipe_name --order_count 5 --order_run_count 2

    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)

        if order_count <= 0:
            raise click.ClickException('order_count must be an integer greater than 0')

        if order_run_count <= 0:
            raise click.ClickException('order_count must be an integer greater than 0')

        click.secho('%s - Get Order information for Kitchen %s' % (get_datetime(), use_kitchen), fg='green')

        check_and_print(
                DKCloudCommandRunner.list_order(backend.dki, use_kitchen, order_count, order_run_count, start, recipe=recipe))
    except Exception as e:
        raise click.ClickException(str(e))


# --------------------------------------------------------------------------------------------------------------------
#  Vault commands
# --------------------------------------------------------------------------------------------------------------------

@dk.command(name='vault-info')
@click.option('--kitchen', '-k', required=False, help='Kitchen name')
@click.option('--global-secrets', '-g', is_flag=True, required=False, help='list global secrets')
@click.pass_obj
def vault_info(backend, global_secrets, kitchen):
    """
    List vault info

    Examples:

        \b
        1) Get global vault info
        dk vault-info

        \b
        2) Get kitchen specific vault info
        dk vault-info -k my-kitchen

        \b
        3) Get kitchen specific and global vault info
        dk vault-info -g -k my-kitchen

    """
    try:
        if not kitchen:
            global_secrets = True
        click.echo(click.style('%s - Getting the vault info' % get_datetime(), fg='green'))
        click.echo(DKCloudCommandRunner.vault_info(backend.dki, global_secrets, kitchen))
    except Exception as e:
        raise click.ClickException(str(e))

@dk.command(name='vault-config')
@click.option('--kitchen', '-k', required=False, help='Kitchen name')
@click.option('--inherit', '-h', default=False, is_flag=True, required=False, help='Configuration inherited from parent kitchen')
@click.option('--service', '-s', required=False, help='Service can be custom or default')
@click.option('--url', '-u', required=False, help='Vault url (with port)')
@click.option('--token', '-t', required=False, help='Vault token')
@click.option('--prefix', '-r', required=False, help='Vault prefix, if exist')
@click.option('--private', '-p', default='False', required=False, help='Whether vault is private or not')
@click.option('--inheritable', '-i', default='False', required=False, help='Whether vault Values are Inheritable or not')
@click.option('--disable', '-d', default=False, is_flag=True, required=False, help='Disable global vault')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def vault_config(backend, kitchen, inherit, service, url, token, prefix, private, inheritable, disable, yes):
    """
    Configure vault. Your role must be "IT" or "ADMIN" to run global vault configuration.

    Examples:

        \b
        1a) Global vault config
        dk vault-config --url http://dummy-vault-url:8200 --token my-vault-token

        \b
        1b) Global vault config: disable
        dk vault-config --disable

        \b
        2) Kitchen vault config with default service
        dk vault-config --kitchen my-kitchen --service default

        \b
        3) Kitchen vault config with configuration inherited from parent
        dk vault-config --kitchen my-kitchen --inherit

        \b
        4) Kitchen vault config with custom service
        dk vault-config --kitchen my-kitchen \\
            --prefix my-kitchen-prefix \\
            --private True \\
            --service custom \\
            --token my-vault-token \\
            --inheritable True \\
            --url http://dummy-vault-url:8200

        \b
        Note: To continue the command in next line, use
            \\ (in Linux)
            or
            ^ (in Windows)

    """
    try:
        for item in [private, inheritable]:
            error_message = 'private and inheritable need to be set to "True" or "False"'
            if item.lower() not in ['true', 'false']: raise click.ClickException(error_message)

        if not kitchen and not (backend.dki.is_user_role('IT') or backend.dki.is_user_role('ADMIN')):
            raise click.ClickException('You do not have IT or ADMIN privileges to run this command for global vault.')

        param_dict = {
            'service': service if service else 'default',
            'url': url if url else '',
            'token': token if token else '',
            'prefix': prefix if prefix else '',
            'private': True if private.lower() == 'true' else False,
            'inheritable': True if inheritable.lower() == 'true' else False
        }

        if param_dict['service'] not in set(['default', 'custom']):
            raise click.ClickException('service needs to be either "default" or "custom"')

        # Global configuration checks
        if not kitchen:
            if service == 'custom':
                raise click.ClickException('--service "custom" does not apply for global vault config')

            if not disable and not url and not token:
                raise click.ClickException('You need to configure url and token to proceed.')

            if not yes:
                message = 'You are configuring the global vault!. Are you sure you want to proceed? [yes/No]'
                confirm = raw_input(message)
                if confirm.lower() != 'yes':
                    return

            if disable:
                param_dict = {
                    'disabled':  disable
                }

        # Kitchen configuration checks
        if kitchen:
            if disable:
                raise click.ClickException('Kitchen vault cannot be disabled. Check vault-delete command instead.')
            if inherit:
                if any([service, url, token, prefix, private.lower() == 'true', inheritable.lower() == 'true']):
                    raise click.ClickException('When inherit is selected: service, url, token, prefix, private and inheritable cannot be set.')

                try:
                    DKCloudCommandRunner.vault_delete(backend.dki, kitchen)
                except Exception as e:
                    if 'No configuration exists' not in str(e): raise e

                click.echo('Done.')
                return

            if service == 'default':
                if any([url, token, prefix, private.lower() == 'true', inheritable.lower() == 'true']):
                    raise click.ClickException('When service is default: url, token, prefix, private and inheritable cannot be set.')

        click.echo(click.style('%s - Setting the vault info' % get_datetime(), fg='green'))
        click.echo(DKCloudCommandRunner.vault_config(backend.dki, kitchen, param_dict))
    except Exception as e:
        raise click.ClickException(str(e))

@dk.command(name='vault-delete')
@click.option('--kitchen', '-k', required=True, help='Kitchen name')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def vault_delete(backend, kitchen, yes):
    """
    Delete kitchen vault configuration.

    Example:

        \b
        dk vault-delete -k my-kitchen
    """
    try:
        if not yes:
            message = 'You are deleting kitchen vault config for kitchen %s!. Are you sure you want to proceed? [yes/No]' % kitchen
            confirm = raw_input(message)
            if confirm.lower() != 'yes':
                return

        click.echo(click.style('%s - Deleting the vault configuration for kitchen %s' % (get_datetime(), kitchen), fg='green'))
        click.echo(DKCloudCommandRunner.vault_delete(backend.dki, kitchen))
    except Exception as e:
        raise click.ClickException(str(e))

# --------------------------------------------------------------------------------------------------------------------
#  Secret commands
# --------------------------------------------------------------------------------------------------------------------
@dk.command(name='secret-list')
@click.option('--kitchen', '-k', required=False, help='Kitchen name')
@click.option('--global-secrets', '-g', is_flag=True, required=False, help='list global secrets')
@click.argument('path', required=False)
@click.pass_obj
def secret_list(backend, path, global_secrets, kitchen):
    """
    List Secrets

    Examples:

        \b
        1) List all global Secrets
        dk secret-list

        \b
        2) List all global Secrets starting for a given secret path
        dk secret-list path

        \b
        3) List Secrets related to a specific kitchen
        dk secret-list -k my-kitchen

        \b
        4) List Secrets related to a specific kitchen, but include global secrets as well
        dk secret-list -k my-kitchen -g

        \b
        5) List Secrets related to a specific kitchen, but include global secrets as well, provide a path
        dk secret-list -k my-kitchen -g sftp/

    """
    try:
        DKCloudCommandRunner.check_secret_path(path)

        if not kitchen:
            global_secrets = True
        click.echo(click.style('%s - Getting the list of secrets' % get_datetime(), fg='green'))
        click.echo(DKCloudCommandRunner.secret_list(backend.dki, path, global_secrets, kitchen))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='secret-write')
@click.argument('entry', required=True)
@click.option('--kitchen', '-k', required=False, help='Kitchen name')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def secret_write(backend, entry, yes, kitchen):
    """
    Write one secret to the Vault. Spaces are not allowed.

    Examples:

        \b
        1) Write global Secret my-key
        dk secret-write my-key=my-value

        \b
        2) Write kitchen specific Secret my-key
        dk secret-write -k my-kitchen my-key=my-value

        \b
        3) Write Secret my-key with file as value
        dk secret-write my-key=@example-file.pem


    """
    try:
        path,value=entry.split('=')
        DKCloudCommandRunner.check_secret_path(path)

        if value.startswith('@'):
            with open(value[1:]) as vfile:
                value = vfile.read()

        secret_exists, _ = DKCloudCommandRunner.secret_exists(backend.dki, path, kitchen)

        if kitchen and not DKCloudCommandRunner.is_vault_config_writable(backend.dki, kitchen):
            raise click.ClickException('No vault service configured for kitchen %s, or vault is read only.' % kitchen)

        # If secret already exists, prompt confirmation message
        if secret_exists:
            if not yes:
                confirm = raw_input('Are you sure you want to overwrite the existing Vault Secret %s ? [yes/No]' % path)
                if confirm.lower() != 'yes':
                    return

        click.echo(click.style('%s - Writing secret' % get_datetime(), fg='green'))
        check_and_print(DKCloudCommandRunner.secret_write(backend.dki, path, value, kitchen))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='secret-delete')
@click.argument('path', required=True)
@click.option('--kitchen', '-k', required=False, help='Kitchen name')
@click.option('--yes', '-y', default=False, is_flag=True, required=False, help='Force yes')
@click.pass_obj
def secret_delete(backend, path, kitchen, yes):
    """
    Delete a secret

    Examples:

        \b
        1) Delete global Secret my-key
        dk secret-delete my-key

        \b
        2) Delete kitchen specific Secret my-key
        dk secret-delete -k my-kitchen my-key

    """
    try:
        if path is None:
            raise click.ClickException('invalid path %s' % path)
        DKCloudCommandRunner.check_secret_path(path)

        if kitchen and not DKCloudCommandRunner.is_vault_config_writable(backend.dki, kitchen):
            raise click.ClickException('No vault service configured for kitchen %s, or vault is read only.' % kitchen)

        if not yes:
            confirm = raw_input('Are you sure you want to delete Secret %s? [yes/No]' % path)
            if confirm.lower() != 'yes':
                return

        click.echo(click.style('%s - Deleting secret' % get_datetime(), fg='green'))
        check_and_print(DKCloudCommandRunner.secret_delete(backend.dki,path, kitchen))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='secret-exists')
@click.option('--kitchen', '-k', required=False, help='Kitchen name')
@click.argument('path', required=True)
@click.pass_obj
def secret_exists(backend, path, kitchen):
    """
    Checks if a secret exists

    Examples:

        \b
        1) Delete global secret my-key
        dk secret-exists my-key

        \b
        2) Delete kitchen specific secret my-key
        dk secret-exists -k my-kitchen my-key

    """
    try:
        DKCloudCommandRunner.check_secret_path(path)
        if kitchen:
            message = '%s Checking secret in kitchen vault %s' % (get_datetime(), kitchen)
        else:
            message = '%s Checking secret in global vault' % get_datetime()
        click.echo(click.style(message , fg='green'))
        _, output_message = DKCloudCommandRunner.secret_exists(backend.dki, path, kitchen)
        click.echo(output_message)
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='kitchen-settings-get')
@click.pass_obj
def kitchen_settings_get(backend):
    """
    Get Kitchen Settings (kitchen-settings.json) for your customer account.
    This file is global to all Kitchens.  Your role must be "IT" or "ADMIN" to get
    the kitchen-settings.json file.
    """
    try:
        if not (backend.dki.is_user_role('IT') or backend.dki.is_user_role('ADMIN')):
            raise click.ClickException('You do not have IT or ADMIN privileges to run this command')

        kitchen = 'master'

        click.secho("%s - Getting a local copy of kitchen-settings.json" % get_datetime(), fg='green')
        check_and_print(DKCloudCommandRunner.kitchen_settings_get(backend.dki, kitchen))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='kitchen-settings-update')
@click.argument('filepath', required=True, nargs=-1)
@click.pass_obj
def kitchen_settings_update(backend, filepath):
    """
    Upload Kitchen Settings (kitchen-settings.json) for your customer account.
    This file is global to all Kitchens.  Your role must be "IT" or "ADMIN" to upload
    the kitchen-settings.json file.
    """
    try:
        if not (backend.dki.is_user_role('IT') or backend.dki.is_user_role('ADMIN')):
            raise click.ClickException('You do not have IT or ADMIN privileges to run this command')

        kitchen = 'master'

        click.secho("%s - Updating the settings" % get_datetime(), fg='green')
        check_and_print(DKCloudCommandRunner.kitchen_settings_update(backend.dki, kitchen, filepath))
    except Exception as e:
        raise click.ClickException(str(e))


@dk.command(name='agent-status')
@click.pass_obj
def agent_status(backend):
    """
    Provides information about the agent status.

    """
    try:

        click.secho("%s - Getting Agent Status Information" % get_datetime(), fg='green')
        data = DKCloudCommandRunner.agent_status(backend.dki)
        click.secho('-----------')
        click.secho('Agent is Online' if data['agent_status']['available'] else 'Agent is Offline - Unable to create new orders')
        click.secho('Total available memory: %d MB' % data['agent_status']['mem'])
        click.secho('Total available disk space: %d MB' % data['agent_status']['disk'])
    except Exception as e:
        raise click.ClickException(str(e))


original_sigint = None


def _get_repo_root_dir(directory):

    if not directory or directory == '/':
        return None
    elif os.path.isdir(os.path.join(directory,'.git')):
        return directory

    parent,_ = os.path.split(directory)
    return _get_repo_root_dir(parent)


HOOK_FILES = ['pre-commit']
GITHOOK_TEMPLATE = """
#!/bin/bash
python -m DKCloudCommand.hooks.DKHooks $0 "$@"
exit $?
"""

def _install_hooks(hooks_dir):

    for hook in HOOK_FILES:
        pre_commit_file = os.path.join(hooks_dir,hook)

        with open(pre_commit_file,'w') as f:
            f.write(GITHOOK_TEMPLATE)

        os.chmod(pre_commit_file,stat.S_IXUSR|stat.S_IRUSR|stat.S_IWUSR)

def _setup_user(repo_dir,config):
    import subprocess
    user = config.get_username()

    subprocess.check_output(['git','config','--local','user.name',user])
    subprocess.check_output(['git','config','--local','user.email',user])

@dk.command(name='git-setup')
@click.pass_obj
def git_setup(backend):
    """
    Set up a GIT repository for DK CLI.
    """
    repo_root_dir = _get_repo_root_dir(os.getcwd())

    if not repo_root_dir:
        raise click.ClickException('You are not in a git repository')

    hooks_dir = os.path.join(repo_root_dir,'.git','hooks')

    _install_hooks(hooks_dir)
    _setup_user(repo_root_dir,backend.dki.get_config())
    pass

# http://stackoverflow.com/questions/18114560/python-catch-ctrl-c-command-prompt-really-want-to-quit-y-n-resume-executi
def exit_gracefully(signum, frame):
    global original_sigint
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    DKCloudCommandRunner.stop_watcher()
    signal(SIGINT, original_sigint)
    question = False
    if question is True:
        try:
            if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
                exit(1)
        except (KeyboardInterrupt, SystemExit):
            print("Ok ok, quitting")
            exit(1)
    else:
        print("Ok ok, quitting now")
        DKCloudCommandRunner.join_active_serving_watcher_thread_join()
        exit(1)
    # restore the exit gracefully handler here
    signal(SIGINT, exit_gracefully)


# https://chriswarrick.com/blog/2014/09/15/python-apps-the-right-way-entry_points-and-scripts/
def main(args=None):
    global original_sigint

    if args is None:
        args = sys.argv[1:]
        Backend(only_check_version=True)   # force to check version

    # store the original SIGINT handler
    original_sigint = getsignal(SIGINT)
    signal(SIGINT, exit_gracefully)

    dk(prog_name='dk')


if __name__ == "__main__":
    main()
