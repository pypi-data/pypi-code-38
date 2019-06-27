"""Status plugin for VSS CLI (vss-cli)."""
import logging

import click
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.sstatus import check_status

_LOGGING = logging.getLogger(__name__)


@click.group(
    'status',
    invoke_without_command=True,
    short_help='Check VSS Status.'
)
@pass_context
def cli(ctx: Configuration):
    """Check VSS Status from https://www.systemstatus.utoronto.ca/"""
    ctx.set_defaults()
    with ctx.spinner(disable=ctx.debug):
        obj = check_status()
    ctx.status = obj
    if click.get_current_context().invoked_subcommand is None:
        columns = [
            ('NAME', 'component.name'),
            ('DESCRIPTION', 'component.description'),
            ('STATUS', 'component.status'),
            ('UPDATED', 'component.updated_at'),
            ('MAINTENANCE', 'upcoming_maintenances[*].name')
        ]
        click.echo(
            format_output(
                ctx,
                [obj],
                columns=columns,
                single=True
            )
        )


@cli.command('maint')
@pass_context
def get_maintenance(ctx: Configuration):
    columns = [
        ('NAME', 'name'),
        ('IMPACT', 'impact'),
        ('STATUS', 'status'),
        ('DESCRIPTION', 'description[0:100]'),
        ('SCHEDULED', 'scheduled_for')
    ]
    columns = ctx.columns or columns
    if ctx.status:
        dat = ctx.status.get('upcoming_maintenances')
        click.echo(
            format_output(
                ctx,
                dat,
                columns=columns,
            )
        )
