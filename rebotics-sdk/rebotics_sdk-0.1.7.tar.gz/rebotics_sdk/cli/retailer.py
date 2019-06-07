import json
import os
from multiprocessing import Pool

import click
from prettytable import PrettyTable

from rebotics_sdk.cli.common import shell, roles, configure
from rebotics_sdk.cli.utils import process_role, read_saved_role
from .renderers import format_processing_action_output
from .utils import ReboticsCLIContext, pass_rebotics_context, app_dir
from ..providers import RetailerProvider, ProviderHTTPClientException
from ..utils import download_file, mkdir_p, \
    get_filename_from_url


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='retailers.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('retailer'), help="Key to specify what retailer to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Retailer CLI tool to communicate with retailer API
    """
    process_role(ctx, role, 'retailer')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=RetailerProvider
    )


@api.command()
@pass_rebotics_context
def version(ctx):
    """Show retailer backend version"""
    click.echo(ctx.provider.version())


@api.command()
@click.option('-t', '--input_type')
@click.option('-s', '--store', type=click.INT)
@click.argument('files', nargs=-1, required=True, type=click.File('rb'))
@pass_rebotics_context
def upload_files(ctx, input_type, store, files):
    """
    Upload processing files to the retailer backend, that can be used as processing action inputs
    """
    file_ids = []
    for f_ in files:
        response = ctx.provider.processing_upload(
            store, f_, input_type
        )
        file_ids.append(response['id'])

        if ctx.verbose:
            click.echo(response)  # redirecting this output to stderr
    click.echo(' '.join(map(str, file_ids)))


REQUEUE_TYPES = {
    "facenet_kf": 'requeue_for_facenet_keyframes_key',
    "pt_multiclass": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS',
    "pt_heatmap": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS_HEATMAP',
    "pt_voting": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS_VOTING',
}


def task_requeue_processing(d):
    provider = d['provider']
    response = provider.requeue(d['id'], d['requeue_type'])
    if d['verbose']:
        click.echo(response)
        click.echo(response['id'])
    return response


def task_cancel_processing(d):
    provider = d['provider']
    response = provider.cancel(d['id'])
    if d['verbose']:
        click.echo(response)
        click.echo(response['id'])
    return response


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-t', '--requeue-type', type=click.Choice(choices=REQUEUE_TYPES.keys()), required=False, default=None)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def requeue(ctx, processing_ids, requeue_type, concurrency):
    """Requeue processing actions by given IDs"""
    task_arguments = []

    for id_ in processing_ids:
        if ctx.verbose:
            click.echo('Requeue for %d' % id_)

        task_arguments.append({
            'verbose': ctx.verbose,
            'provider': ctx.provider,
            'id': id_,
            'requeue_type': REQUEUE_TYPES.get(requeue_type)
        })

    pool = Pool(concurrency)
    actions_list = pool.map(task_requeue_processing, task_arguments)

    format_processing_action_output(actions_list, ctx.format)


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def cancel(ctx, processing_ids, concurrency):
    """Cancel processing of the actions by given IDs"""
    task_arguments = []

    for id_ in processing_ids:
        if ctx.verbose:
            click.echo('Requeue for %d' % id_)

        task_arguments.append({
            'verbose': ctx.verbose,
            'provider': ctx.provider,
            'id': id_,
        })

    pool = Pool(concurrency)
    actions_list = pool.map(task_cancel_processing, task_arguments)

    format_processing_action_output(actions_list, ctx.format)


@api.command()
@click.option('-t', '--input_type')
@click.option('-s', '--store', type=click.INT)
@click.option('-p', '--store-planogram', type=click.INT)
@click.option('--aisle')
@click.option('--section')
@click.option('-l', '--lens-used', is_flag=True, default=False)
@click.argument('files', nargs=-1, required=True, type=click.INT)
@pass_rebotics_context
def create_processing_action(ctx, input_type, store, store_planogram, aisle, section, lens_used, files):
    """Create processing action for store defining files by IDs"""
    response = ctx.provider.create_processing_action(
        store, files, input_type,
        store_planogram=store_planogram,
        aisle=aisle,
        section=section,
        lens_used=lens_used
    )
    if ctx.verbose:
        click.echo(response, )
    click.echo(response['id'])


def download_file_from_dict(d):
    ctx = d['ctx']
    if ctx.verbose:
        click.echo('>> Downloading file into %s' % d['filepath'], err=True)
    result = download_file(d['url'], d['filepath'])
    click.echo('<< Downloaded file into %s' % d['filepath'], err=True)
    return result


def task_download_processing_action(ctx, processing_action_id):
    return ctx.provider.processing_action_detail(processing_action_id)


@api.command()
@click.argument('actions', nargs=-1, required=True, type=click.INT)
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def download_processing_action(ctx, actions, target, concurrency):
    """Download processing actions by given IDs"""
    files_to_download = []

    pool = Pool(concurrency)
    actions_data = pool.starmap(task_download_processing_action, [(ctx, action) for action in actions])
    if ctx.verbose:
        click.echo('GET API for processing actions completed')

    for data in actions_data:
        action_id = data['id']
        processing_action_folder = os.path.join(target, 'ProcessingAction#%d' % action_id)

        mkdir_p(processing_action_folder)
        results = os.path.join(processing_action_folder, 'results')
        inputs = os.path.join(processing_action_folder, 'inputs')

        mkdir_p(results)
        mkdir_p(inputs)

        for key in ['merged_image_jpeg', 'merged_image', ]:
            files_to_download.append({
                'url': data[key],
                'filepath': os.path.join(results, get_filename_from_url(data[key])),
                'ctx': ctx,
            })

        for input_object in data.get('inputs', []):
            files_to_download.append({
                'filepath': os.path.join(inputs, get_filename_from_url(input_object['file'])),
                'url': input_object['file'],
                'ctx': ctx
            })

        with open(os.path.join(processing_action_folder, 'processing_action_%d.json' % action_id), 'w') as fout:
            json.dump(data, fout, indent=4)

        if ctx.verbose:
            click.echo('Downloading files for %s' % (action_id,))

    pool.map(download_file_from_dict, files_to_download)

    if ctx.verbose:
        click.echo('Processing download success')


@api.command()
@click.argument('actions', nargs=-1, required=True, type=click.INT)
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@click.option('--template', default="{action_id}_{i}.{ext}")
@pass_rebotics_context
def download_processing_inputs(ctx, actions, target, concurrency, template):
    """Download processing inputs from processing actions"""
    files_to_download = []

    pool = Pool(concurrency)
    actions_data = pool.starmap(task_download_processing_action, [(ctx, action) for action in actions])

    if ctx.verbose:
        click.echo('GET API for processing actions completed')

    for data in actions_data:
        for i, input_object in enumerate(data.get('inputs', [])):
            filename = get_filename_from_url(input_object['file'])
            ext = filename.split('.')[-1]
            action_id = data['id']
            files_to_download.append({
                'filepath': os.path.join(target, template.format(action_id=action_id, i=i, ext=ext)),
                'url': input_object['file'],
                'ctx': ctx
            })

    if ctx.verbose:
        click.echo("Task registraion completed")

    pool.map(download_file_from_dict, files_to_download)

    if ctx.verbose:
        click.echo('Processing inputs download success')


def upload_preview_task(d):
    provider = d['provider']
    images_path = d['images_path']
    upc = d['upc']
    delete = d['delete']

    if delete:
        try:
            response = provider.delete_product_previews(upc)
            click.echo('Deleted %s previews for product %s' % (response['deleted'], upc,), err=True)
        except ProviderHTTPClientException:
            click.echo('Product with UPC %s does not exists' % upc, err=True)

    for image_path in images_path:
        with open(image_path, 'rb') as image:
            try:
                provider.upload_product_preview(upc, image)
            except ProviderHTTPClientException as e:
                click.echo("xxx Failed to send image: %s" % image_path)
                click.echo(str(e), err=True)
            click.echo('<< Uploaded product preview for %s from %s' % (upc, image_path), err=True)


@api.command()
@click.option('-d', '--delete', is_flag=True)
@click.option('-c', '--concurrency', type=int, default=4)
@click.argument('path', type=click.Path(exists=True), default=os.getcwd())
@pass_rebotics_context
def upload_previews_from_folder(ctx, delete, concurrency, path):
    """
    Upload previews from file system to the server in parallel
    It has increased retries and timeout
    """
    provider = ctx.provider
    provider.retries = 5
    provider.timeout = 300
    verbose = ctx.verbose

    tasks = []
    for label in os.listdir(path):
        upc_folder = os.path.join(path, label)
        if not os.path.isdir(upc_folder):
            continue

        if verbose:
            click.echo('Reading folder: %s' % upc_folder)
        task = {
            'provider': provider,
            'images_path': [],
            'delete': delete,
            'upc': label
        }

        if label.isdigit():
            for filename in os.listdir(upc_folder):
                image_path = os.path.join(upc_folder, filename)

                if os.path.isfile(image_path):
                    task['images_path'].append(image_path)

        if task['images_path']:
            tasks.append(task)

    if verbose:
        click.echo('Number of tasks: {}'.format(len(tasks)))

    p = Pool(concurrency)
    p.map(upload_preview_task, tasks)
    click.echo('Finished')


PROCESSING_STATUSES = {
    'created': 'action created',
    'done': 'done',
    'error': 'error',
    'interrupted': 'interrupted',
    'progress': "in progress",
}


@api.command()
@click.option('-s', '--store', type=click.INT, help='Store ID')
@click.option('--status', type=click.Choice(PROCESSING_STATUSES.keys()))
@click.option('-p', '--page', type=click.INT, default=1)
@click.option('-r', '--page-size', type=click.INT, default=10)
@pass_rebotics_context
def processing_actions(ctx, store, status, page, page_size):
    """Fetches processing actions and renders them in terminal"""
    table = PrettyTable()
    table.field_names = ['#', 'id', 'store', 'user', 'status',
                         'created', 'last_requeue', 'last_requeue ago', 'time in queue']

    if ctx.verbose:
        click.echo('Getting list of processing actions')
    data = ctx.provider.get_processing_action_list(
        store,
        PROCESSING_STATUSES.get(status),
        page=page,
        page_size=page_size,
    )
    click.echo('Total results: %d' % len(data))
    if ctx.format != 'id':
        format_processing_action_output(data, 'id')
    format_processing_action_output(data, ctx.format)


@api.command()
@click.option('-t', '--token')
@click.argument('url')
@pass_rebotics_context
def set_webhook(ctx, token, url):
    """Setting webhook url for current user"""
    data = ctx.provider.set_webhook(url, token)
    click.echo('Webhook ID on server is : %d' % data['id'])


@api.command()
@click.option('-t', '--title', help='Planogram title', required=True)
@click.option('-d', '--description', help='Planogram description', default='')
@click.argument('planogram_file', type=click.File(mode='rb'))
@pass_rebotics_context
def import_planogram(ctx, planogram_file, title, description):
    """Upload planogram file to retailer instance in a very specific format"""
    try:
        ctx.provider.import_planogram(planogram_file, title, description)
    except (AssertionError, ProviderHTTPClientException) as exc:
        click.echo(exc, err=True)


@api.command()
@click.argument('planogram_assign_file', type=click.File(mode='r'))
@click.option('-d', '--deactivate', is_flag=True, help='Deactivate old planogram')
@pass_rebotics_context
def assign_planogram_through_file(ctx, planogram_assign_file, deactivate):
    try:
        ctx.provider.assign_planogram(planogram_assign_file, deactivate)
    except (AssertionError, ProviderHTTPClientException) as exc:
        click.echo(exc, err=True)


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
