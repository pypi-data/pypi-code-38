# -*- coding: utf-8 -*-
"""Utility functions to import archives, such as export archives"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import tarfile
import zipfile

from aiida.common.archive import extract_tar, extract_zip
from aiida.common.exceptions import NotExistent
from aiida.common.folders import SandboxFolder
from aiida.common import json


def get_archive_file(archive, core_file=False):
    """
    Return the absolute path of the archive file used for testing purposes. The expected path for these files:

        aiida-export_migration-testing.archives

    :param archive: the relative filename of the archive
    :param core_file: Whether or not the file is located in aiida_core repo or the current repo.
    :returns: absolute filepath of the archive test file
    """
    import inspect

    if core_file:
        # Add filepath to aiida_core repo
        aiida_fixtures_path = os.path.join(
            os.path.dirname(inspect.getabsfile(json)), os.path.pardir,
            "backends/tests/fixtures/export/migrate")

        dirpath_archive = os.path.join(aiida_fixtures_path, archive)
    else:
        # Add filepath to local repo
        dirpath_current = os.path.dirname(os.path.realpath(__file__))
        dirpath_archives = os.path.join(dirpath_current, 'archives')

        dirpath_archive = os.path.join(dirpath_archives, archive)

    if not os.path.isfile(dirpath_archive):
        dirpath_parent = os.path.dirname(dirpath_archive)
        raise ValueError(
            'archive {} does not exist in the archives directory {}'.format(
                archive, dirpath_parent))

    return dirpath_archive


def get_json_files(archive, silent=True, core_file=False):
    """Get metadata.json and data.json from an exported AiiDA archive

    :param archive: the relative filename of the archive
    :param silent: Whether or not the extraction should be silent
    :param core_file: Whether or not the file is located in aiida_core repo or the current repo.
    """
    # Get archive
    dirpath_archive = get_archive_file(archive, core_file=core_file)

    # Unpack archive
    with SandboxFolder(sandbox_in_repo=False) as folder:
        if zipfile.is_zipfile(dirpath_archive):
            extract_zip(dirpath_archive, folder, silent=silent)
        elif tarfile.is_tarfile(dirpath_archive):
            extract_tar(dirpath_archive, folder, silent=silent)
        else:
            raise ValueError(
                'invalid file format, expected either a zip archive or gzipped tarball'
            )

        try:
            with io.open(
                    folder.get_abs_path('data.json'), 'r',
                    encoding='utf8') as fhandle:
                data = json.load(fhandle)
            with io.open(
                    folder.get_abs_path('metadata.json'), 'r',
                    encoding='utf8') as fhandle:
                metadata = json.load(fhandle)
        except IOError:
            raise NotExistent(
                'export archive does not contain the required file {}'.format(
                    fhandle.filename))

    # Return metadata.json and data.json
    return metadata, data


def migrate_archive(input_file, output_file, silent=True):
    """Migrate contents using `migrate_recursively`
    This is essentially similar to `verdi export migrate`.
    However, since this command may be disabled, this function simulates it and keeps the tests working.

    :param input_file: filename with full path for archive to be migrated
    :param output_file: filename with full path for archive to be created after migration
    """
    from aiida.cmdline.utils.migration import migrate_recursively

    # Unpack archive, migrate, and re-pack archive
    with SandboxFolder(sandbox_in_repo=False) as folder:
        if zipfile.is_zipfile(input_file):
            extract_zip(input_file, folder, silent=silent)
        elif tarfile.is_tarfile(input_file):
            extract_tar(input_file, folder, silent=silent)
        else:
            raise ValueError(
                'invalid file format, expected either a zip archive or gzipped tarball'
            )

        try:
            with io.open(
                    folder.get_abs_path('data.json'), 'r',
                    encoding='utf8') as fhandle:
                data = json.load(fhandle)
            with io.open(
                    folder.get_abs_path('metadata.json'), 'r',
                    encoding='utf8') as fhandle:
                metadata = json.load(fhandle)
        except IOError:
            raise NotExistent(
                'export archive does not contain the required file {}'.format(
                    fhandle.filename))

        # Migrate
        migrate_recursively(metadata, data, folder)

        # Write json files
        with io.open(folder.get_abs_path('data.json'), 'wb') as fhandle:
            json.dump(data, fhandle, indent=4)

        with io.open(folder.get_abs_path('metadata.json'), 'wb') as fhandle:
            json.dump(metadata, fhandle, indent=4)

        # Pack archive
        compression = zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(
                output_file, mode='w', compression=compression,
                allowZip64=True) as archive:
            src = folder.abspath
            for dirpath, dirnames, filenames in os.walk(src):
                relpath = os.path.relpath(dirpath, src)
                for filename in dirnames + filenames:
                    real_src = os.path.join(dirpath, filename)
                    real_dest = os.path.join(relpath, filename)
                    archive.write(real_src, real_dest)
