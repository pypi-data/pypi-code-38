# Copyright (C) 2017-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
import tempfile

import patoolib
import shutil


def tmp_extract(archive, dir=None, prefix=None, suffix=None, log=None,
                source=None):
    """Extract an archive to a temporary location with optional logs.

    Args:
        archive (string): Absolute path of the archive to be extracted
        prefix (string): Optional modifier to the temporary storage
            directory name. (I guess in case something
            goes wrong and you want to go look?)
        log (python logging instance): Optional for recording extractions.
        source (string): Optional source URL of the archive for adding to
            log messages.
    Returns:
        A context manager for a temporary directory that automatically
        removes itself. See: help(tempfile.TemporaryDirectory)
    """
    logstr = 'From %s - ' % source if log and source else ''

    if dir and not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)

    archive_base = os.path.basename(archive)
    if archive_base[0] == '.':
        package = '.' + archive_base.split('.')[1]
    else:
        package = archive_base.split('.')[0]

    tmpdir = tempfile.mkdtemp(dir=dir, prefix=prefix, suffix=suffix)
    repo_path = os.path.join(tmpdir, package)
    try:
        patoolib.extract_archive(archive, interactive=False, outdir=tmpdir)
    except Exception as e:
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)
        msg = '%sFailed to uncompress archive %s at %s - %s' % (
            logstr, archive_base, repo_path, e)
        raise ValueError(msg)

    if log:
        log.info('%sUncompressing archive %s at %s' % (
            logstr, archive_base, repo_path))
    return tmpdir
