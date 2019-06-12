# -*- coding: utf-8 -*-
from os.path import normpath

import click

from spell.api import models
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.log import logger
from spell.cli.utils import (
    convert_to_local_time,
    prettify_size,
    right_arrow,
    truncate_string,
)
from spell.cli.commands.link import format_link_display as format_link_display


# display order of columns
COLUMNS = [
    "size",
    "date",
    "path",
]


@click.command(name="ls",
               short_help="List resource files")
@click.argument("path", default="")
@click.option("-h", "human_readable", help="Display file sizes in human-readable format",
              is_flag=True, default=False)
@click.pass_context
def ls(ctx, path, human_readable):
    """
    List resource files for datasets, run outputs, and uploads.

    Resources are the generic name for datasets, models, or any other files that
    can be made available to a run. Spell keeps these organized for you in a
    remote filesystem that is browsable with the `ls` command, with the resources
    placed into directories that reflect their origin.

    There are many ways resources are generated. The user can upload resources
    directly with `spell upload` or execute a run with `spell run` that writes
    files to disk. Spell also provides a number of publicly-accessible datasets.
    """
    if path:
        path = normpath(path)

    # grab the ls from the API
    client = ctx.obj["client"]

    def format_ls_line(ls_line):
        utf8 = ctx.obj["utf8"]

        if ls_line.date:
            ls_line.date = convert_to_local_time(ls_line.date, include_seconds=False)
        else:
            ls_line.date = "-"

        if ls_line.size is None:
            ls_line.size = "-"
        elif human_readable:
            ls_line.size = prettify_size(ls_line.size)

        status_suffix = ""
        if ls_line.additional_info:
            status_suffix = " ({})".format(ls_line.additional_info)

        if ls_line.link_target:
            status_suffix = u" {} {}".format(right_arrow(utf8), ls_line.link_target)

        ls_line.date = truncate_string(ls_line.date, 14, fixed_width=True, utf8=utf8)
        ls_line.size = truncate_string(ls_line.size, 8, fixed_width=True, utf8=utf8)
        term_w = click.get_terminal_size()[0]
        max_suffix_w = term_w - 30 - 8 - 14 - 2  # This is two less the sum of width of all strings above
        if (max_suffix_w > 0):
            ls_line.path += truncate_string(status_suffix, max_suffix_w, fixed_width=False, utf8=utf8)
        return " ".join([ls_line.size, ls_line.date, ls_line.path])

    found_a_line = False
    with api_client_exception_handler():
        logger.info("Retrieving resource list from Spell")
        link = None
        for l in client.get_ls(path):
            found_a_line = True
            if isinstance(l, models.Error):
                raise ExitException(l.status)
            elif type(l) == dict:
                link = l
            else:
                click.echo(format_ls_line(l))
        if link is not None:
            term_size = click.get_terminal_size()[0]
            size = max(term_size//2, min(50, term_size))
            divider = '-'*size
            click.echo(divider)
            if link["resource_path"] != path:
                expansion = path[len(link["alias"]):]
                link["alias"] = path
                link["resource_path"] = "".join([link["resource_path"], expansion])
            display_lines = format_link_display(ctx, [link], ls_display=True)
            click.echo(display_lines[0])
    if not found_a_line:
        click.echo("No files for path {}".format(path), err=True)
        return
