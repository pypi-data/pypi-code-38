"""
    These are the sub-commands for a top level object added to the CLI group in 'cli.py'.
    The commands and options are implemented here and the logic behind them resides in the corresponding behavior file.
"""

from cli import pyke, behavior
import click

@click.group('component-set-version', help="A component-set-version is where the platform looks for components when used in a widget.\
The version also contains other details like CSS includes.")
def component_set_version():
    pass

@click.command('ls')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--component-set', '-cs', prompt=True, help='The id or the urlRef of the component-set')
@click.option('--format', '-f', default='{id} {versionNumber} {directIncludes} {directCssIncludes} {label} {expand__experiences} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--filter', default='')
@click.option('--page', default=1)
@click.option('--pagesize', default=100)
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def list(component_set, profile, format, json, **kwargs):
    behavior.ComponentSetVersionBehavior(profile=profile, format=format, json=json, **kwargs).list(component_set)

@click.command('components', help="Given a --component-set and a --version, this will return the raw JSON contained in a component-set-version")
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--component-set', '-cs', prompt=True, help='The id or the urlRef of the component-set the version is associated with')
@click.option('--version', '-v', prompt=True)
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def components(component_set, profile, version, json):
    behavior.ComponentSetVersionBehavior(profile=profile, json=json).list_components(component_set, version)

@click.command('add', help="While adding a new component-set-version you must always upload a zipped file, even if you use the from-version option")
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--component-set', '-cs', prompt=True, help='The id or the urlRef of the component-set the version is added to')
@click.option('--component-set-file-path', '-path', prompt=True, type=click.Path(), help='Must be the path to a zipped file.')
@click.option('--from-version', '-fv', type=str, help="Take all values from an exsisting version and create a new version. \
Increment the major, minor or patch version by 1 with --major, --minor, --patch flags. Override any old values by passing them in as options. \
When using this option with component-sets you will always need to provide a new, zipped, component set file.")
@click.option('--version', '-v', type=str, default=None, help="The version number of the new version")
@click.option('--patch', 'version_bump', flag_value='patch', default=True)
@click.option('--minor', 'version_bump', flag_value='minor')
@click.option('--major', 'version_bump', flag_value='major')
@click.option('--css-includes', type=str, default=None, multiple=True)
@click.option('--direct-includes', type=str, default=None, multiple=True)
@click.option('--label', '-l', type=click.Choice(['prod', 'dev', 'old']))
@click.option('--format', '-f', default='{id} {versionNumber} {directIncludes} {directCssIncludes} {label} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def create(component_set, profile, component_set_file_path, from_version, version,
    version_bump, css_includes, direct_includes, label, format, json):
    behavior.ComponentSetVersionBehavior(profile=profile, format=format, json=json)\
        .create(component_set, component_set_file_path, from_version, version,
            version_bump, css_includes, direct_includes, label)

@click.command()
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--component-set', '-cs', prompt=True, help='The id or the urlRef of the component-set the version is associated with')
@click.option('--version', '-v', prompt=True, help='The ID or the version-number of the version to update')
@click.option('--label', '-l', prompt=True, type=str)
@click.option('--format', '-f', default='{id} {versionNumber} {directIncludes} {directCssIncludes} {label} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def update(component_set, version, label, profile, format, json):
    behavior.ComponentSetVersionBehavior(profile=profile, format=format, json=json).update(component_set, version, label)

@click.command('rm')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--component-set', '-cs', prompt=True, help='The id or the urlRef of the component-set the version is associated with')
@click.option('--version-mask', '-vm', help="Delete versions with version numbers that match this version mask")
@click.option('--version', '-v', help='The version ID or the version-number')
@click.option('--format', '-f', default='{id} {versionNumber} {directIncludes} {directCssIncludes} {label} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def delete(component_set, version_mask, version, profile, format, json):
    behavior.ComponentSetVersionBehavior(profile=profile, format=format, json=json).delete(component_set, version, version_mask)

component_set_version.add_command(list)
component_set_version.add_command(create)
component_set_version.add_command(delete)
component_set_version.add_command(update)
component_set_version.add_command(components)
