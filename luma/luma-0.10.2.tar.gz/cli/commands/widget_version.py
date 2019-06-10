"""
    These are the sub-commands for a top level object added to the CLI group in 'cli.py'.
    The commands and options are implemented here and the logic behind them resides in the corresponding behavior file.
"""

from cli import pyke, behavior
import click

@click.group('widget-version', help="A widget-version is the docker image of widget, \
along with the details it needs to run such as, port number and Env variables.")
def widget_version():
  pass

@click.command('ls')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'widget', prompt=True)
@click.option('--format', '-f', default='{id} {actualState} {versionNumber} {label} {isEditable} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--filter', default='')
@click.option('--page', default=1)
@click.option('--pagesize', default=100)
@click.option('--json/--table', default=False)
@pyke.auth.profile_context_required
def list(widget, profile, format, json, **kwargs):
  behavior.WidgetVersionBehavior(profile=profile, format=format, json=json, **kwargs).list(widget)

@click.command('start')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'widget', prompt=True)
@click.option('--version', '-v', prompt=True, help='The version ID or the version-number')
@click.option('--format', '-f', default='{id} {actualState} {versionNumber} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False)
@pyke.auth.profile_context_required
def start(widget, version, profile, format, json):
  behavior.WidgetVersionBehavior(profile=profile, format=format, json=json).start_stop("start", widget, version)

@click.command('stop')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'widget', prompt=True)
@click.option('--version', '-v', prompt=True, help='The version ID or the version-number')
@click.option('--format', '-f', default='{id} {actualState} {versionNumber} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False)
@pyke.auth.profile_context_required
def stop(widget, version, profile, format, json):
  behavior.WidgetVersionBehavior(profile=profile, format=format, json=json).start_stop("stop", widget, version)

@click.command('exec', help='Pass in a command to be run directly on the docker container.')
@click.argument('command')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'widget', prompt=True)
@click.option('--version', '-v', prompt=True, help='The version ID or the version-number')
@click.option('--json/--table', default=False)
@pyke.auth.profile_context_required
def run(command, widget, version, profile, json):
  behavior.WidgetVersionBehavior(profile=profile, json=json).run(widget, version, command)

@click.command('logs')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'widget', prompt=True)
@click.option('--version', '-v', prompt=True, help='The version ID or the version-number')
@click.option('--json/--table', default=False)
@pyke.auth.profile_context_required
def logs(widget, version, profile, json):
  behavior.WidgetVersionBehavior(profile=profile, json=json).logs(widget, version)

@click.command('add')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', prompt=True)
@click.option('--port', type=int, help='The port to expose on your container')
@click.option('--editor-port', type=int, help="The port to connect to the container's editor")
@click.option('--is-editable', is_flag=True, help="Set if this is an editable container. Must come from a version with an editor port")
@click.option('--docker-image', '-image', type=str, help='The name (including the tag) of a docker image from the docker daemon. You must have docker running locally to use this option.')
@click.option('--container-file-path', '-path', type=click.Path(), help='The image must be a gzipped tar file. Ex: {file_name}.tar.gz')
@click.option('--from-version', '-fv', type=str, help="Take all values from an exsisting version and create a new version. \
Increment the major, minor or patch version by 1 with --major, --minor, --patch flags. Override any old values by passing them in as options.")
@click.option('--version', '-v', type=str, default=None, help="The version number of the new version")
@click.option('--patch', 'version_bump', flag_value='patch', default=True)
@click.option('--minor', 'version_bump', flag_value='minor')
@click.option('--major', 'version_bump', flag_value='major')
@click.option('--env-var', 'env', default=None, multiple=True, help="The environment variables to add to the docker image when it is run. It must be valid json wrapped in single quotes.")
@click.option('--label', '-l', type=click.Choice(['prod', 'dev', 'old']))
@click.option('--format', '-f', default='{id} {actualState} {versionNumber} {label} {isEditable} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def create(**kwargs):
  behavior.ContainerVersionBehavior(**kwargs).create('widget')

@click.command()
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'widget', prompt=True)
@click.option('--version', '-v', prompt=True, help='The version ID or the version-number')
@click.option('--label', '-l', prompt=True)
@click.option('--format', '-f', default='{id} {versionNumber} {label} {isEditable} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False)
@pyke.auth.profile_context_required
def update(widget, version, label, profile, format, json):
  behavior.WidgetVersionBehavior(profile=profile, json=json).update(widget, version, label, format)

@click.command('rm')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'widget', prompt=True)
@click.option('--version-mask', '-vm', type=str, help="Delete versions with version numbers that match this version mask")
@click.option('--version', '-v', help='The version ID or the version-number')
@click.option('--format', '-f', default='{id} {versionNumber} {label} {isEditable} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False)
@pyke.auth.profile_context_required
def delete(widget, version_mask, version, profile, format, json):
  behavior.WidgetVersionBehavior(profile=profile, json=json).delete(widget, version, version_mask, format)

widget_version.add_command(list)
widget_version.add_command(create)
widget_version.add_command(start)
widget_version.add_command(stop)
widget_version.add_command(delete)
widget_version.add_command(update)
widget_version.add_command(run)
widget_version.add_command(logs)
