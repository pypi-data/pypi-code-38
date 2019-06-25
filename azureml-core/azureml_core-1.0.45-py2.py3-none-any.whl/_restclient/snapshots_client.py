# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Access ArtifactsClient"""

import os
import requests
import json
import uuid
import tempfile

from azureml._file_utils import download_file, get_path_size

from .workspace_client import WorkspaceClient

from azureml._base_sdk_common.common import get_http_exception_response_string
from azureml._base_sdk_common.merkle_tree import DirTreeJsonEncoder, create_merkletree
from azureml._base_sdk_common.merkle_tree_differ import compute_diff
from azureml._base_sdk_common.project_snapshot_cache import ContentSnapshotCache
from azureml._base_sdk_common.snapshot_dto import SnapshotDto
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._base_sdk_common.utils import create_session_with_retry
from azureml._project.ignore_file import get_project_ignore_file
from azureml.exceptions import SnapshotException, ProjectSystemException

SNAPSHOT_MAX_FILES = 2000
SNAPSHOT_BATCH_SIZE = 500
ONE_MB = 1024 * 1024
SNAPSHOT_MAX_SIZE_BYTES = 300 * ONE_MB


class SnapshotsClient(WorkspaceClient):
    """
    Snapshot client class

    :param service_context:
    :type service_context: azureml._restclient.service_context.ServiceContext
    """
    def __init__(self, *args, **kwargs):
        super(SnapshotsClient, self).__init__(*args, **kwargs)
        self._cache = ContentSnapshotCache(self._service_context)

    def _validate_snapshot_size(self, file_or_folder_path, exclude_function, raise_on_validation_failure):
        size = get_path_size(file_or_folder_path,
                             size_limit=SNAPSHOT_MAX_SIZE_BYTES, exclude_function=exclude_function)
        if size > SNAPSHOT_MAX_SIZE_BYTES:
            error_message = "====================================================================\n" \
                            "\n" \
                            "While attempting to take snapshot of {}\n" \
                            "Your total snapshot size exceeds the limit of {} MB.\n" \
                            "Please see http://aka.ms/aml-largefiles on how to work with large files.\n" \
                            "\n" \
                            "====================================================================\n" \
                            "\n".format(file_or_folder_path, SNAPSHOT_MAX_SIZE_BYTES / ONE_MB)
            if raise_on_validation_failure:
                raise SnapshotException(error_message)
            else:
                self._logger.warning(error_message)

    def create_snapshot(self, file_or_folder_path, retry_on_failure=True, raise_on_validation_failure=True):
        auth_headers = self.auth.get_authentication_header()

        ignore_file = get_project_ignore_file(file_or_folder_path)
        exclude_function = ignore_file.is_file_excluded

        self._validate_snapshot_size(file_or_folder_path, exclude_function, raise_on_validation_failure)

        # Get the previous snapshot for this project
        parent_root, parent_snapshot_id = self._cache.get_latest_snapshot()

        # Compute the dir tree for the current working set
        curr_root = create_merkletree(file_or_folder_path, exclude_function)

        # Compute the diff between the two dirTrees
        entries = compute_diff(parent_root, curr_root)

        # If there are no changes, just return the previous snapshot_id
        if not len(entries):
            return parent_snapshot_id

        entries_to_send = [entry for entry in entries if
                           (entry.operation_type == 'added' or entry.operation_type == 'modified') and entry.is_file]

        if len(entries_to_send) > SNAPSHOT_MAX_FILES and not os.environ.get("AML_SNAPSHOT_NO_FILE_LIMIT"):
            error_message = "====================================================================\n" \
                            "\n" \
                            "While attempting to take snapshot of {}\n" \
                            "Your project exceeds the file limit of {}.\n" \
                            "\n" \
                            "====================================================================\n" \
                            "\n".format(file_or_folder_path, SNAPSHOT_MAX_FILES)
            if raise_on_validation_failure:
                raise SnapshotException(error_message)
            else:
                print(error_message)

        custom_headers = {
            "dirTreeRootFile": "true"
        }

        dir_tree_file_contents = json.dumps(curr_root, cls=DirTreeJsonEncoder)

        # Git metadata
        snapshot_properties = global_tracking_info_registry.gather_all(file_or_folder_path)

        with create_session_with_retry() as session:

            # There is an OS limit on how many files can be open at once, so we must batch the snapshot to not exceed
            # the limit. We take multiple snapshots, each building on each other, and return the final snapshot.
            new_snapshot_id = None
            # We always need to do at least one pass,
            # for the case where the only change is deleted files in dirTreeRootFile
            first_pass = True
            while len(entries_to_send) or first_pass:
                first_pass = False
                files_to_send = []
                files_to_close = []
                if new_snapshot_id:
                    parent_snapshot_id = new_snapshot_id
                new_snapshot_id = str(uuid.uuid4())
                try:
                    # Add entries until we hit batch limit
                    while len(files_to_send) < SNAPSHOT_BATCH_SIZE and len(entries_to_send):
                        entry = entries_to_send.pop()
                        path_env = (os.path.join(file_or_folder_path, entry.node_path)
                                    if os.path.isdir(file_or_folder_path)
                                    else entry.node_path)
                        file_obj = open(path_env, "rb")
                        files_to_send.append(("files", (entry.node_path, file_obj)))
                        files_to_close.append(file_obj)

                    # directory_tree needs to be added to all snapshot requests
                    files_to_send.append(
                        ("files", ("dirTreeRootFile", dir_tree_file_contents, "application/json", custom_headers)))
                    files_to_send.append(("properties", (None, json.dumps(snapshot_properties))))

                    url = self._service_context._get_project_content_url() + "/content/v1.0" + \
                        self._service_context._get_workspace_scope() + "/snapshots/" + \
                        new_snapshot_id + "?parentSnapshotId=" + parent_snapshot_id

                    response = self._execute_with_base_arguments(
                        session.post, url, files=files_to_send, headers=auth_headers)
                    if response.status_code >= 400:
                        if retry_on_failure:
                            # The cache may have been corrupted, so clear it and try again.
                            self._cache.remove_latest()
                            return self.create_snapshot(file_or_folder_path, retry_on_failure=False)
                        else:
                            raise SnapshotException(get_http_exception_response_string(response))
                finally:
                    for f in files_to_close:
                        f.close()

        # Update the cache
        snapshot_dto = SnapshotDto(dir_tree_file_contents, new_snapshot_id)
        self._cache.update_cache(snapshot_dto)
        return new_snapshot_id

    def get_rest_client(self, user_agent=None):
        return self._service_context._get_project_content_restclient(user_agent=user_agent)

    def restore_snapshot(self, snapshot_id, path):
        headers = self.auth.get_authentication_header()

        with create_session_with_retry() as session:
            url = self._service_context._get_project_content_url() + "/content/v1.0" + \
                self.get_workspace_uri_path() + "/snapshots/" + snapshot_id
            response = self._execute_with_base_arguments(session.get, url, headers=headers)
            # This returns a sas url to blob store
            response.raise_for_status()
            sas_url = response.content.decode('utf-8')
            sas_url = sas_url[1:-1]
            snapshot_file_name = str(snapshot_id) + '.zip'
            if path is None:
                path = tempfile.gettempdir()

            temp_path = os.path.join(path, snapshot_file_name)

            try:
                download_file(sas_url, temp_path, session=session)
            except requests.HTTPError as http_error:
                raise ProjectSystemException(http_error.strerror)

        return os.path.abspath(temp_path)
