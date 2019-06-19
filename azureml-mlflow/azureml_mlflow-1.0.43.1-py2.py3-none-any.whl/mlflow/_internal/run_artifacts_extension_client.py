# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Access run artifacts extension client."""

import os

from io import IOBase

from azureml._async import TaskQueue
from azureml._file_utils import upload_blob_from_stream
from azureml.exceptions import UserErrorException, AzureMLException

from azureml._restclient.models.artifact_path_dto import ArtifactPathDto
from azureml._restclient.models.batch_artifact_create_command import BatchArtifactCreateCommand

from azureml._restclient.run_artifacts_client import RunArtifactsClient, SUPPORTED_NUM_EMPTY_ARTIFACTS


class RunArtifactsExtensionClient(RunArtifactsClient):
    """Run Artifacts Extension client class."""

    def download_artifact(self, run_id, path, output_file_path):
        """
        Download a single artifact from artifact service.

        :param run_id: the run id of the run that's associated with the artifact
        :type run_id: str
        :param path: the filepath within the container of the artifact to be downloaded
        :type path: str
        :param output_file_path: filepath in which to store the downloaded artifact locally
        :rtype: None
        """
        filename = os.path.basename(path)  # save outputs/filename.txt as filename.txt
        if os.path.isdir(output_file_path):
            self._logger.debug("output_file_path for download_artifact is a directory.")
            output_file_path = os.path.join(output_file_path, filename)
        else:
            self._logger.debug("output_file_path for download_artifact is not a directory.")
        super(RunArtifactsExtensionClient, self).download_artifact(run_id, path, output_file_path)

    def create_empty_artifacts(self, run_id, paths):
        """Create empty artifacts."""
        if run_id is None:
            raise UserErrorException("run_id cannot be null when creating empty artifacts")

        if isinstance(paths, str):
            paths = [paths]
        artifacts = [ArtifactPathDto(path) for path in paths]
        batch_create_command = BatchArtifactCreateCommand(artifacts)
        res = self._execute_with_experiment_arguments(
            self._client.run_artifact.batch_create_empty_artifacts,
            run_id,
            batch_create_command)

        if res.errors:
            error_messages = []
            for artifact_name in res.errors:
                error = res.errors[artifact_name].error
                error_messages.append("{}: {}".format(error.code,
                                                      error.message))
            raise AzureMLException("\n".join(error_messages))

        return res

    def upload_stream_to_existing_artifact(self, stream, artifact, content_information,
                                           content_type=None, session=None):
        """Upload a stream to existring artifact."""
        artifact = artifact
        artifact_uri = content_information.content_uri
        session = session if session is not None else self.session
        res = upload_blob_from_stream(stream, artifact_uri, content_type=content_type, session=session)
        return res

    def upload_artifact_from_stream(self, stream, run_id, name, content_type=None, session=None):
        """Upload a stream to a new artifact."""
        if run_id is None:
            raise UserErrorException("Cannot upload artifact when run_id is None")
        # Construct body
        res = self.create_empty_artifacts(run_id, name)
        artifact = res.artifacts[name]
        content_information = res.artifact_content_information[name]
        self.upload_stream_to_existing_artifact(stream, artifact, content_information,
                                                content_type=content_type, session=session)
        return res

    def upload_artifact_from_path(self, path, *args, **kwargs):
        """Upload a local file to a new artifact."""
        path = os.path.normpath(path)
        path = os.path.abspath(path)
        with open(path, "rb") as stream:
            return self.upload_artifact_from_stream(stream, *args, **kwargs)

    def upload_artifact(self, artifact, *args, **kwargs):
        """Upload local file or stream to a new artifact."""
        self._logger.debug("Called upload_artifact")
        if isinstance(artifact, str):
            self._logger.debug("Uploading path artifact")
            return self.upload_artifact_from_path(artifact, *args, **kwargs)
        elif isinstance(artifact, IOBase):
            self._logger.debug("Uploading io artifact")
            return self.upload_artifact_from_stream(artifact, *args, **kwargs)
        else:
            raise UserErrorException("UnsupportedType: type {} is invalid, "
                                     "supported input types: file path or file".format(type(artifact)))

    def upload_files(self, paths, run_id, names=None):
        """
        Upload files to artifact service.

        :rtype: list[BatchArtifactContentInformationDto]
        """
        if run_id is None:
            raise UserErrorException("run_id cannot be null when uploading artifact")

        names = names if names is not None else paths
        path_to_name = {}
        paths_and_names = []
        # Check for duplicates, this removes possible interdependencies
        # during parallel uploads
        for path, name in zip(names, paths):
            if path not in path_to_name:
                paths_and_names.append((path, name))
                path_to_name[path] = name
            else:
                self._logger.warning("Found repeat file {} with name {} in upload_files.\n"
                                     "Uploading file {} to the original name "
                                     "{}.".format(path, name, path, path_to_name[path]))

        batch_size = SUPPORTED_NUM_EMPTY_ARTIFACTS

        results = []
        for i in range(0, len(names), batch_size):
            with TaskQueue(worker_pool=self._pool, _ident="upload_files", _parent_logger=self._logger) as task_queue:
                batch_names = names[i:i + batch_size]
                batch_paths = paths[i:i + batch_size]

                content_information = self.create_empty_artifacts(run_id, batch_names)

                def perform_upload(path, artifact, artifact_content_info, session):
                    with open(path, "rb") as stream:
                        return self.upload_stream_to_existing_artifact(stream, artifact, artifact_content_info,
                                                                       session=session)

                for path, name in zip(batch_paths, batch_names):
                    artifact = content_information.artifacts[name]
                    artifact_content_info = content_information.artifact_content_information[name]
                    task = task_queue.add(perform_upload, path, artifact, artifact_content_info, self.session)
                    results.append(task)

        return map(lambda task: task.wait(), results)

    def upload_dir(self, dir_path, run_id, path_to_name_fn=None):
        """
        Upload all files in path.

        :rtype: list[BatchArtifactContentInformationDto]
        """
        if run_id is None:
            raise UserErrorException("Cannot upload when run_id is None")
        paths_to_upload = []
        names = []
        for pathl, _subdirs, files in os.walk(dir_path):
            for _file in files:
                fpath = os.path.join(pathl, _file)
                paths_to_upload.append(fpath)
                if path_to_name_fn is not None:
                    name = path_to_name_fn(fpath)
                else:
                    name = fpath
                names.append(name)
        self._logger.debug("Uploading {}".format(names))
        result = self.upload_files(paths_to_upload, run_id, names)
        return result
