# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.


import click

# short aliases for all commands
_aliases = dict()


def get_cmd_name(in_alias=None):
    """Get the full command name of an alias. If the argument is not
    the alias of a command or the full name then return None.

    Arguments:
    in_alias -- String with alias of a command or the full name of the
    command.

    Returns:
    String with the full command name or None if the alias does not map to
    a command.
    """
    retval = None
    if (in_alias and
            in_alias in _aliases.keys()):
        retval = _aliases.get(in_alias)
    elif (in_alias and
            in_alias in _aliases.values()):
        retval = in_alias
    return retval


def set_alias(in_alias=None, in_cmd_name=None):
    """Sets the alias for a full command name.

    Arguments:
    in_alias -- Alias name.
    in_cmd_name -- Full name of the command.

    Returns:
    True if the alias was set correctly, otherwise false.
    """
    retval = False
    if (in_alias and
            in_cmd_name and
            in_alias not in _aliases.keys()):
        _aliases[in_alias] = in_cmd_name
        retval = True
    return retval


@click.command(name='list-aliases')
def list_aliases():
    """List all of the aliases available for full command names."""
    click.echo('Available command aliases:')
    for key, value in _aliases.items():
        click.echo('    {0} {1}'.format(key, value))
