import click
from missinglink.core.context import Expando

from missinglink.commands.utilities import CommonOptions
from .resources import resources_commands


@resources_commands.group('azure')
@click.option('--location', envvar="ML_AZURE_LOCATION", help='Azure location to use.', default='eastus', required=False)
@click.pass_context
def azure_commands(ctx, **kwargs):
    ctx.obj.azure = Expando()
    ctx.obj.azure.location = kwargs.pop('location', None)


@azure_commands.command('init', help='Initialize Resource Management on Azure, creating the cloud connection and the default queue and resource group.')
@CommonOptions.org_option()
@click.option('--location', envvar="ML_AZURE_LOCATION", help='Azure location to use.', required=False)
@click.option('--queue', required=False)
@click.option('--acr', help='Azure Container Registry name to use in jobs.', required=False, multiple=True)
@click.pass_context
def init(ctx, **kwargs):
    ctx.obj.azure.location = kwargs.pop('location', None) or ctx.obj.azure.location
    from missinglink.commands.cloud.azure.azure_context import AzureContext

    azure_context = AzureContext(ctx, kwargs)

    queue = azure_context.kwargs.get('queue')
    if queue:
        # This will fail when the group is not present
        azure_context.get_queue(queue)

    if azure_context.kwargs.get('acr'):
        azure_context.authorise_acr(kwargs['acr'])
    else:
        azure_context.init_and_authorise_app()
