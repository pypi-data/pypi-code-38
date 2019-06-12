import click

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_CONFIG,
)
from spell.cli.utils import (
    convert_to_local_time,
    right_arrow,
    truncate_string,
)


@click.command(name="link", short_help="List symlinks, find symlinks by alias, or create a symlink to a resource path.")
@click.argument("alias", required=False, default=None)
@click.argument("resource_path", required=False, default=None)
@click.pass_context
def link(ctx, alias, resource_path):
    """
    With no argument, displays all existing symlinks.

    With a single argument, searches through server database for a symlink with a
    specific alias ALIAS.

    With two arguments, creates a symlink with alias ALIAS to a finished run
    uploaded resource, or public dataset with path RESOURCE_PATH.
    Note: ALIAS must NOT contain any of the following: / . " \\ [ ] : ; | = ,
    """
    if alias is not None:
        if resource_path is not None:
            createLink(ctx, alias, resource_path)
        else:
            findLink(ctx, alias)
    else:
        listLinks(ctx)


def check_for_forbidden_chars(string):
    forbidden_chars = set(list('/."\\[]:;|=,'))  # forbidden characters in link_name
    if len(forbidden_chars.intersection(set(list(string)))) > 0:
        msg = 'Forbidden character. Link aliases must not contain any of the following: /."\\[]:;|=,'
        raise ExitException(msg, SPELL_INVALID_CONFIG)


def format_link_display(ctx, links, ls_display=False):
    utf8 = ctx.obj["utf8"]
    display_lines = []
    width = max([len(l["alias"]) + len(l["resource_path"]) for l in links]) + 10  # plus extra whitespace
    for l in links:
        link_info = " ".join([l["alias"], right_arrow(utf8), l["resource_path"]])
        if not ls_display:
            date = convert_to_local_time(l["created_at"], include_seconds=False)
            link_info = truncate_string(link_info, width, fixed_width=True, utf8=utf8)
            date = truncate_string(date, 14, fixed_width=True, utf8=utf8)
            display_lines.append("".join([link_info, date]))
        else:
            link_info = truncate_string(link_info, width, fixed_width=True, utf8=utf8)
            display_lines.append(link_info)
    return display_lines


def createLink(ctx, alias, resource_path):
    client = ctx.obj["client"]
    if alias in ('public', 'runs', 'uploads'):
        msg = 'Forbidden alias. Link aliases must not correspond to existing directories.'
        raise ExitException(msg, SPELL_INVALID_CONFIG)
    check_for_forbidden_chars(alias)
    with api_client_exception_handler():
        link = client.create_link(resource_path, alias)
        display_lines = format_link_display(ctx, [link])
        click.echo("Successfully created symlink:")
        click.echo(display_lines[0])


def findLink(ctx, alias):
    client = ctx.obj["client"]
    with api_client_exception_handler():
        check_for_forbidden_chars(alias)
        link = client.get_link(alias)
        if len(link) > 0:
            display_lines = format_link_display(ctx, [link])
            click.echo(display_lines[0])
        else:
            click.echo("No links with alias {} found.".format(alias))


def listLinks(ctx):
    client = ctx.obj["client"]
    with api_client_exception_handler():
        links = client.list_links()
        if len(links) > 0:
            display_lines = format_link_display(ctx, links)
            for line in display_lines:
                click.echo(line)
        else:
            click.echo("No symlinks found!")
            click.echo("Use the command 'spell link [ALIAS] [RESOURCE_PATH]' to create a symlink to a resource.")
