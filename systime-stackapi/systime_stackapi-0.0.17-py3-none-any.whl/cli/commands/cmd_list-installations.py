import click
import json
from systime_stackapi.cli.stackcli import pass_context, StackHelper
from systime_stackapi.stackService import StackService

stack_helper = StackHelper()

@click.command('list-installations', short_help='List installations.')
@click.option('--output-format', type=click.Choice(choices=['json', 'plain']), default='plain', help="How to format output.")
@pass_context
def cli(ctx, output_format):
    """Gets a list of all installations."""

    installations = ctx.stack_helper.get_installation_name_list()

    if output_format == 'plain':
        for installation in installations:
            click.echo('{}'.format(installation))

    if output_format == 'json':
        click.echo(json.dumps(installations))
