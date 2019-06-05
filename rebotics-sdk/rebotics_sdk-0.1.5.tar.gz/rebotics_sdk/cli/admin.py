import datetime
import os
from functools import partial
from multiprocessing.pool import Pool

import click
import humanize
from prettytable import PrettyTable

from rebotics_sdk.cli.common import shell
from .utils import ReboticsCLIContext, app_dir, pass_rebotics_context
from ..providers import AdminProvider, RetailerProvider, ProviderHTTPClientException
from ..providers.facenet import FacenetProvider
from ..utils import Timer


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']), help='Result rendering')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='admin.json', help="Specify what config.json to use")
@click.option('-r', '--role', required=True, help="Key to specify what admin to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Admin CLI tool to communicate with dataset API
    """
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=AdminProvider
    )


@api.command()
@click.option('-h', '--host', help='admin host', prompt=True)
@click.option('-u', '--user', prompt=True, )
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=False)
@pass_rebotics_context
def configure(ctx, user, password, host):
    """Fetch token, save it and use the role of it"""
    provider = ctx.provider_class(host=host)
    ctx.update_configuration(
        host=host,
    )
    try:
        response = provider.token_auth(user, password)
    except ProviderHTTPClientException:
        click.echo('Failed to login')
        return

    ctx.update_configuration(
        host=host,
        **response
    )
    click.echo(response, err=True)
    click.echo('Saved configuration for {} admin in {}'.format(ctx.key, ctx.config.filepath))


def get_retailer_version_task(retailer_dict):
    retailer_provider = RetailerProvider(host=retailer_dict['host'], retries=1)
    try:
        response = retailer_provider.version()
        version = response['version']
        uptime = humanize.naturaldelta(datetime.timedelta(seconds=int(response['uptime'])))
    except Exception:
        version = 'not working'
        uptime = '---'

    d = [
        retailer_dict['codename'],
        retailer_dict['title'],
        version,
        uptime,
        retailer_dict['host'],
    ]
    return d


@api.command()
@pass_rebotics_context
def retailer_versions(ctx):
    """Fetch retailer versions and their meta information"""
    provider = ctx.provider
    retailers = provider.get_retailer_list()

    pool = Pool(len(retailers))
    results = pool.map(get_retailer_version_task, retailers)

    table = PrettyTable()
    table.field_names = ['codename', 'title', 'version', 'uptime', 'host']
    for result in results:
        table.add_row(result)
    click.echo(table)


def load_models(ctx, retailer_id, retailer_secret):
    provider = ctx.provider
    provider.set_retailer_identifier(retailer_id, retailer_secret)
    return provider.get_retailer_tf_models()


@api.command()
@click.option('-r', '--retailer-id', help='Retailer id')
@click.option('-s', '--retailer-secret', help='Retailer secret key')
@click.option('-u', '--facenet-url', help='Facenet service URL')
@click.argument('image_url')
@pass_rebotics_context
def extract_feature_vectors(ctx, retailer_id, retailer_secret, facenet_url, image_url):
    """Fetches latest configuration of neural model for retailer by it's ID and Secret key;
    Sends image to facenet to load model into state."""
    models = load_models(ctx, retailer_id, retailer_secret)

    facenet_model = models['facenet_model']
    click.echo("Facenet model: %s" % facenet_model['codename'])
    facenet_provider = FacenetProvider(facenet_url)

    feature_extractor = partial(
        facenet_provider.extract_from_image_url,
        model_path=facenet_model['data_path'],
        index_path=facenet_model['index_path'],
        meta_path=facenet_model['meta_path'],
    )

    with Timer() as t:
        result = feature_extractor(image_url)
    if ctx.verbose:
        click.echo(result)
    click.echo("Elapsed: %s seconds" % t.elapsed_secs)


api.add_command(shell, 'shell')
