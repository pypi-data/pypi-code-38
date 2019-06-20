import os
import shutil
from multiprocessing.pool import Pool

import click
import requests
from tqdm import tqdm

from rebotics_sdk.cli.common import shell, configure, roles
from .utils import ReboticsCLIContext, pass_rebotics_context, app_dir, read_saved_role, process_role
from ..providers import DatasetProvider
from ..utils import download_file, mkdir_p


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='dataset.json', help="Specify what config.json to use")
@click.option('-r', '--role',  default=lambda: read_saved_role('dataset'), help="Key to specify what dataset to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Dataset CLI tool to communicate with dataset API
    """
    process_role(ctx, role, 'dataset')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=DatasetProvider
    )


def save_image_task(d):
    download_file(d['url'], d['filepath'])
    click.echo('Downloaded jpeg image to {}'.format(d['filepath']))


@api.command()
@click.argument('meta_data_url', )
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def setup_training_dir(ctx, meta_data_url, target, concurrency):
    """Set up training directory"""
    click.echo("Downloading meta data from {}".format(meta_data_url), err=True)
    response = requests.get(meta_data_url)
    response.raise_for_status()

    meta_data = response.json()
    click.echo("Downloaded meta data from {}".format(meta_data_url), err=True)

    mkdir_p(target)
    annotations_path = os.path.join(target, 'Annotations')
    mkdir_p(annotations_path)
    images_path = os.path.join(target, 'JPEGImages')
    mkdir_p(images_path)
    image_sets_path = os.path.join(target, 'ImageSets')
    mkdir_p(image_sets_path)
    main_path = os.path.join(image_sets_path, 'Main')
    mkdir_p(main_path)

    for file_in_main in meta_data['main']:
        with open(os.path.join(main_path, file_in_main['filename']), 'w') as fout:
            fout.write(file_in_main['value'])

    for annotation_file in meta_data['annotations']:
        with open(os.path.join(annotations_path, annotation_file['filename']), 'w') as fout:
            fout.write(annotation_file['value'])

    click.echo("Saved annotation files. Fetching images...", err=True)

    p = Pool(concurrency)
    jpeg_images = [
        {
            'url': i['url'],
            'filepath': os.path.join(images_path, i['image_name'])
        } for i in meta_data['jpeg_images']
    ]
    p.map(save_image_task, jpeg_images)


@api.command()
@click.argument('ref_upc', type=click.File())
@click.argument('ref_features', type=click.File())
@click.option('-r', '--retailer', prompt=True, )
@click.option('-f', '--facenet', prompt=True, )
@pass_rebotics_context
def upload_ref(ctx, ref_upc, ref_features, retailer, facenet):
    """Uploads reference UPC and reference features for retailer and facenet to dataset"""
    click.echo('Starting uploading to {provider.host} for {retailer} and {facenet}...'.format(
        provider=ctx.provider, retailer=retailer, facenet=facenet
    ), err=True)

    for upc, feature in tqdm(zip(ref_upc, ref_features)):
        ctx.provider.save_feature_vector(retailer=retailer, facenet=facenet, upc=upc, feature=feature)

    click.echo('Done uploading to {provider.host} for {retailer} and {facenet}!'.format(
        provider=ctx.provider, retailer=retailer, facenet=facenet
    ))


@api.command()
@click.option('-r', '--retailer', prompt=True, )
@click.option('-f', '--facenet', prompt=True, )
@click.argument('output', type=click.Path(), default='.')
@pass_rebotics_context
def download_ref_backup(ctx, retailer, facenet, output):
    """Downloads reference backup for retailer and facenet"""
    filename, raw = ctx.provider.download_reference_database(retailer, facenet)

    if os.path.isdir(output):
        mkdir_p(output)
        output = os.path.join(output, filename)
    elif os.path.isfile(output):
        mkdir_p(os.path.dirname(output))
    else:
        raise OSError('Could not write to path that does not')

    if ctx.verbose:
        click.echo(output)

    with open(output, 'wb') as out_file:
        shutil.copyfileobj(raw, out_file)


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
