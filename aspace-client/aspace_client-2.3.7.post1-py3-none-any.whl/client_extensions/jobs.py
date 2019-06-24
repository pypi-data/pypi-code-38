import json
import os
from typing import Union, List

from aspace import constants, base_client, enums


class JobManagementService(object):
    """
    Contains methods that can be used to create and modify ArchivesSpace jobs.
    """

    def __init__(self, client: base_client.BaseASpaceClient):
        self._client = client

    def import_types(self, repo_uri) -> List[dict]:
        """
        Returns the JSON result from
        `GET /repositories/:repo_id/jobs/import_types`, which should be a list
        of objects with the schema:

        ```
        {
            'description': str,
            'name': str,
        }
        ```
        """
        resp = self._client.get('{}/jobs/import_types'.format(repo_uri))
        assert resp.ok, resp.text
        return resp.json()

    def _create_with_files(self, repo_uri: str,
                           import_type: Union[str, enums.DataImportTypes],
                           filepaths: List[str],) -> dict:
        """

        Creates a new job that operates on a list of input files, taking a list
        of local file paths. Requires a repository URI and a data import type
        (explicit string from `/repositories/:repo_id/jobs/import_types` or
        value from `enums.DataImportTypes`).

        Asserts that the response from the API is a good response, then returns
        the JSON response.

        """

        _import_type = (
            import_type.value
            if isinstance(import_type, enums.DataImportTypes) else
            import_type
            if isinstance(import_type, str) else
            None
        )

        assert _import_type, (
            "Invalid value for 'import_type': {}".format(import_type)
        )

        job = {
            'job_type': 'import_job',
            'job': {
                'jsonmodel_type': 'import_job',
                'filenames': list(map(os.path.basename, filepaths)),
                'import_type': _import_type,
            }
        }

        files = [
            ('files[]', open(filepath, 'r'))
            for filepath in
            filepaths
        ]

        resp = self._client.post(
            '{}/jobs_with_files'.format(repo_uri),
            files=files,
            data={'job': json.dumps(job)},
        )

        assert resp.ok, resp.text
        return resp.json()

    def create_with_files(self, repo_uri: str,
                          import_type: Union[str, enums.DataImportTypes],
                          filepaths: List[str],
                          one_job_per_file: bool = False) -> dict:
        """

        Creates a new job that operates on a list of input files, taking a list
        of local file paths. Requires a repository URI and a data import type
        (explicit string from `/repositories/:repo_id/jobs/import_types` or
        value from `enums.DataImportTypes`).

        Asserts that the response from the API is a good response, then returns
        the JSON response.

        If `:one_job_per_file:` is set to true, returns a list of the JSON
        responses.

        """

        if one_job_per_file:
            return [
                self._create_with_files(repo_uri, import_type, [file])
                for file in
                filepaths
            ]

        return self._create_with_files(repo_uri, import_type, filepaths)
