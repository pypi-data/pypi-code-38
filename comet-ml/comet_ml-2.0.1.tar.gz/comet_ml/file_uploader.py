# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

""" This module handles syncing git repos with the backend. Used for pull
request features."""

import logging
import os
import tempfile
import threading
import zipfile

from ._reporting import FILE_UPLOADED_FAILED
from .connection import Reporting, get_backend_session

LOGGER = logging.getLogger(__name__)


def compress_git_patch(git_patch):
    # Create a zip
    zip_dir = tempfile.mkdtemp()

    zip_path = os.path.join(zip_dir, "patch.zip")
    archive = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    archive.writestr("git_diff.patch", git_patch)
    archive.close()

    return archive, zip_path


def _send_file(url, files, params):
    LOGGER.debug("Uploading file to %s with params %s", url, params)

    with get_backend_session() as session:
        r = session.post(url, params=params, files=files)

    LOGGER.debug("Uploading file to %s done", url)

    if r.status_code != 200:
        raise ValueError(
            "POSTing file failed (%s) on url %r: %s" % (r.status_code, url, r.content)
        )

    return r


def send_file(
    post_endpoint, api_key, experiment_id, project_id, file_path, additional_params=None
):
    params = {"experimentId": experiment_id, "projectId": project_id, "apiKey": api_key}

    if additional_params is not None:
        params.update(additional_params)

    is_file_like = hasattr(file_path, "read")

    if is_file_like:
        files = {"file": file_path}
        return _send_file(post_endpoint, params=params, files=files)
    else:
        with open(file_path, "rb") as _file:
            files = {"file": _file}
            return _send_file(post_endpoint, params=params, files=files)


def upload_file(
    project_id,
    experiment_id,
    file_path,
    upload_endpoint,
    api_key,
    additional_params=None,
    clean=True,
):
    try:
        response = send_file(
            upload_endpoint,
            api_key,
            experiment_id,
            project_id,
            file_path,
            additional_params,
        )

        is_file_like = hasattr(file_path, "read")

        if not is_file_like and clean is True:
            # Cleanup file
            try:
                os.remove(file_path)
            except OSError:
                pass

        LOGGER.debug(
            "File successfully uploaded to (%s): %s",
            response.status_code,
            upload_endpoint,
        )
    except Exception as e:
        LOGGER.error("File could not be uploaded", exc_info=True)
        Reporting.report(
            event_name=FILE_UPLOADED_FAILED,
            experiment_key=experiment_id,
            project_id=project_id,
            api_key=api_key,
            err_msg=str(e),
        )


def upload_file_thread(*args, **kwargs):
    p = threading.Thread(target=upload_file, args=args, kwargs=kwargs)
    p.daemon = True
    p.start()
    return p
