#!/usr/bin/env python
import os
import threading
import textwrap
from multiprocessing.dummy import Pool

import atexit
import click
from tus_client.exceptions import TusCommunicationError, TusUploadFailed
from six.moves import queue
from tempfile import mkdtemp
from shutil import rmtree
import tarfile

from spell.api.exceptions import ClientException, UnauthorizedRequest
from spell.cli.exceptions import api_client_exception_handler
from spell.cli.log import logger
from spell.cli.utils import prettify_size
from spell.cli.exceptions import ExitException
from spell.cli.constants import BLACKLISTED_FILES


NUM_WORKERS = 10


@click.command(name="upload",
               short_help="Upload a file or directory")
@click.argument("path", type=click.Path(exists=True, dir_okay=True, file_okay=True, readable=True), metavar='PATH')
@click.option("-n", "--name", type=str, help="upload name", default=None, metavar='NAME')
@click.option("-c", "--compress", help="compress before uploading", is_flag=True, default=False)
@click.pass_context
def upload(ctx, path, name, compress):
    """
    Upload the contents of PATH to uploads/NAME

    The contents of PATH will be uploaded to Spell and will be accessible at
    uploads/NAME. If NAME is not provided and path is a directory, NAME
    defaults to the the directory name of PATH.  If NAME is not provided
    and PATH is a file, the user is prompted for a NAME.
    """
    # get absolute path
    path = os.path.abspath(os.path.expanduser(path))
    # determine upload name
    is_dir = os.path.isdir(path)
    if name is None:
        if is_dir:
            name = os.path.basename(path)
        else:
            name = click.prompt(click.wrap_text("Enter a name for the upload.\n'{}' will be accessible "
                                "at 'uploads/NAME/{}'".format(path, os.path.basename(path))),
                                default=os.path.basename(os.path.dirname(path)), show_default=True)

    compress_param = "--compress" if compress else ""
    resume_command = "spell upload {} --name '{}' {}".format(compress_param, name, path)
    resume_message = "To resume upload, run \"{}\"".format(resume_command)

    # create the dataset
    client = ctx.obj["client"]
    with api_client_exception_handler():
        logger.info("Creating dataset")
        dataset = client.new_dataset(name, compress)
    logger.info("created dataset {}".format(dataset.name))

    # thread pool to perform the uploads
    pool = Pool(NUM_WORKERS)

    # queue to send progress bar updates on
    q = queue.Queue()

    # generate files to upload and add tasks to the executor
    total_bytes = 0
    uploads = []  # a list of arguments for each file to pass to ds_client.upload_file
    if compress:
        click.echo("Warning: Using compress for upload will require additional "
                   "disk space to store the compressed dataset.")
        temp_dir = mkdtemp(None, "spell-upload-")
        atexit.register(rmtree, temp_dir, ignore_errors=True)
        zip_file_path = os.path.join(temp_dir, "upload.tar.gz")
        if is_dir:
            arcname = "upload"
        else:
            arcname = "upload/" + os.path.basename(path)
        with tarfile.open(zip_file_path, "w:gz") as tar:
            tar.add(path, arcname=arcname)
        uploads.append((zip_file_path, dataset.id, os.path.basename(zip_file_path), q))
        total_bytes += os.path.getsize(zip_file_path)
    else:
        if is_dir:
            for (dirpath, dirnames, filenames) in os.walk(path):
                for f in filenames:
                    if f in BLACKLISTED_FILES:
                        continue
                    fullpath = os.path.join(dirpath, f)
                    relpath = os.path.relpath(fullpath, path)
                    if os.name == "nt":
                        relpath = relpath.replace("\\", "/")
                    uploads.append((fullpath, dataset.id, relpath, q))
                    total_bytes += os.path.getsize(fullpath)
        else:
            uploads.append((path, dataset.id, os.path.basename(path), q))
            total_bytes += os.path.getsize(path)

    click.echo("Total upload size: {}".format(prettify_size(total_bytes)))

    # create thread to update progress
    def update_progress():
        with click.progressbar(length=total_bytes, label="Uploading to uploads/{}".format(name)) as bar:
            while True:
                item = q.get()
                if isinstance(item, int):
                    if int(item) > 0:
                        bar.update(int(item))
                else:
                    break
    t = threading.Thread(target=update_progress)
    t.daemon = True
    t.start()
    try:
        for result in pool.imap_unordered(lambda x: client.upload_file(*x), uploads,
                                          chunksize=max(1, int(len(uploads)/NUM_WORKERS))):
            pass
    except KeyboardInterrupt as e:
        raise ExitException("Upload aborted. {}".format(resume_message))
    except UnauthorizedRequest as e:
        raise ExitException("Login session has expired. Please log in again ('spell login'). {}".format(resume_message))
    except ClientException as e:
        raise ExitException(click.wrap_text("Unexpected upload issue: {}. {}.".format(e.message, resume_message)))
    except TusUploadFailed as e:
        msg = None
        if e.status_code:
            if e.status_code == 423:
                msg = textwrap.dedent("""\
                A file appears to be locked. This could be the result of running 'spell upload'
                on the same set of files. {}""").format(resume_message)
        raise ExitException(msg or click.wrap_text("Unexpected upload issue: {}. {}.".format(e, resume_message)))
    except TusCommunicationError as e:
        msg = None
        if e.status_code:
            if e.status_code == 409:
                msg = textwrap.dedent("""\
                A file appears to have been modified since a previous upload of '{}' was initiated.
                Please restore the upload to its original contents or initiate a new upload under
                a different name. {}.""").format(name, resume_message)
            if e.status_code == 423:
                msg = textwrap.dedent("""\
                A file appears to be locked. This could be the result of running 'spell upload'
                on the same set of files. {}""").format(resume_message)
        raise ExitException(msg or click.wrap_text("Upload issue: {}. {}.".format(e, resume_message)))
    except Exception as e:
        raise ExitException(click.wrap_text("Unexpected upload issue: {}. {}.".format(e, resume_message)))
    finally:
        q.put("exit")
        t.join()
        pool.terminate()

    # complete upload
    client.complete_upload(dataset.id)
    click.echo("Upload of {} ({}) to 'uploads/{}' complete.".format(name, path, name))
