import click

from missinglink.resource_manager.docker.config import ConfigBuilder, config_params, get_active_config
from missinglink.resource_manager.docker.controllers.transport.backbone import Backbone
from missinglink.resource_manager.docker.pip import get_version


@click.group(help='Missing Link Resource Manager version#%s' % get_version())
def cli():
    pass


@cli.command('version')
def print_version():
    click.echo(get_version())


@cli.command('config')
@config_params
def mk_config():
    click.echo('Configuration updated')


@cli.command('run')
def mk_run():
    ConfigBuilder.update({})  # used for configuration migration triggering
    Backbone.run()


@cli.command('job')
@click.option('job', '-j', '--job', required=True, help='Job to execute and exit')
@config_params
def mk_job(job=None):
    active_config = get_active_config()
    active_config.general.pull_job = job
    active_config.general.save()
    click.echo(f'Run job {active_config.general.pull_job}')
    Backbone.run()
    active_config.general.pull_job = None
    active_config.general.save()
    click.echo("Done")
