import os
import zipfile
from os import remove, walk
from os.path import splitext, join, exists, isdir, relpath
from shutil import copyfileobj, move, rmtree

import click
import requests

from kudu.api import request as api_request
from kudu.config import ConfigOption
from kudu.types import PitcherFileType


def move_dir(src, dst):
    for root, dirs, files in walk(src):
        for name in files:
            arcroot = join(dst, relpath(root, src))
            if not exists(arcroot):
                os.makedirs(arcroot)
            move(join(root, name), join(arcroot, name))
    rmtree(src)


def move_thumb(root):
    filename = root + '.png'
    if exists(filename):
        move(filename, 'thumbnail.png')


@click.command()
@click.option('--file', '-f', 'pfile',
              cls=ConfigOption, config_name='file_id',
              prompt='File ID', type=PitcherFileType())
@click.pass_context
def pull(ctx, pfile):
    download_url = api_request('get', '/files/%d/download-url/' % pfile['id'], token=ctx.obj['token']).json()

    with open(pfile['filename'], 'w') as stream:
        r = requests.get(download_url, stream=True)
        copyfileobj(r.raw, stream)

    root, ext = splitext(pfile['filename'])
    if ext == '.zip':
        with zipfile.ZipFile(pfile['filename'], 'r') as stream:
            stream.extractall()
        remove(pfile['filename'])

        if exists('.kudu.yml') and isdir(root):
            move_dir(root, os.curdir if pfile['category'] else 'interface')
            move_thumb(root)
