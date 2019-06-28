import click
import json
from systime_stackapi.cli.stackcli import pass_context, StackHelper
from systime_stackapi.stackService import StackService

stack_helper = StackHelper()

@click.command('typo3config', short_help='Get and/or manipulate typo3config.')
@click.argument('installation', type=click.Choice(choices=stack_helper.get_installation_name_list(True)), nargs=1)
@click.option('--action', type=click.Choice(choices=['print_config', 'edit_config']), default='print_config', help="What to do.")
@pass_context
def cli(ctx, action, installation):
    """Show data on installation."""

    endpoint = ctx.stack_helper.stack_endpoint_from_installation(installation)
    stack_service = ctx.stack_helper.stack_services[endpoint]

    typo3_configuration = stack_service.get_installation_typo3_configuration(installation)
    local_configuration = typo3_configuration['typo3conf/LocalConfiguration.php']


    if action == 'print_config':
        click.echo(local_configuration)
        exit(0)

    if action == 'edit_config':
        new_config = click.edit(local_configuration)
        if new_config is None:
            click.echo()
            click.echo(click.style('Update was cancelled.', fg='red'))
            exit(0)

        stack_service.update_installation_typo3_configuration(installation, new_config)
        click.echo(click.style('File was updated', fg='yellow'))


