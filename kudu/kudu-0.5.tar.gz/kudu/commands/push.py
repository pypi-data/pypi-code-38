import os
import tempfile
import zipfile
from datetime import datetime

import click
import requests

from kudu.api import request as api_request
from kudu.config import ConfigOption
from kudu.types import PitcherFileType


@click.command()
@click.option('--file', '-f', 'pfile',
              cls=ConfigOption, config_name='file_id',
              prompt=True, type=PitcherFileType(category=('zip', 'presentation')))
@click.pass_context
def push(ctx, pfile):
    chroot, ext = os.path.splitext(pfile['filename'])

    with tempfile.NamedTemporaryFile() as tf:
        zf = zipfile.ZipFile(tf.name, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(os.getcwd()):
            arcroot = os.path.relpath(root)
            for name in files:
                arcname = name if not (arcroot == os.curdir and name == 'thumbnail.png') else chroot + '.png'
                zf.write(os.path.join(root, name), os.path.join(chroot, arcroot, arcname))
        zf.close()

        upload_url = api_request('get', '/files/%d/upload-url/' % pfile['id'], token=ctx.obj['token']).json()
        requests.put(upload_url, data=tf)

    api_request('patch', '/files/%d/' % pfile['id'], json={'creationTime': datetime.utcnow().isoformat()},
                token=ctx.obj['token'])
