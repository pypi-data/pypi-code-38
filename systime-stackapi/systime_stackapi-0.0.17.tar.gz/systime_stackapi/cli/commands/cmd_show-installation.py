import click
import json
from systime_stackapi.cli.stackcli import pass_context, StackHelper
from systime_stackapi.stackService import StackService

stack_helper = StackHelper()

@click.command('show-installation', short_help='Get data on installation.')
@click.argument('installation', type=click.Choice(choices=stack_helper.get_installation_name_list(True)), nargs=-1)
@click.option('--output-format', type=click.Choice(choices=['json', 'plain']), default='plain', help="How to format output.")
@pass_context
def cli(ctx, output_format, installation):
    """Show data on installation."""
    installation_parameters = installation
    installation_list = ctx.stack_helper.get_installations()

    filtered_list = []

    for installation in installation_list:
        if installation['InstallationName'] in installation_parameters:
            filtered_list.append(installation)

    if output_format == 'plain':
        for installation in filtered_list:
            click.echo('')
            click.echo(click.style('{}'.format(installation['InstallationName']), fg='green'))
            for key, value in installation['Context'].items():
                click.echo('{}: {}'.format(key, value))

    if output_format == 'json':
        click.echo(json.dumps(filtered_list))
