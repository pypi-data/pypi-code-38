from contextlib import contextmanager
import json
import tarfile

from spell.api import base_client, models
from spell.api.exceptions import ClientException, JsonDecodeError
from spell.api.utils import url_path_join

RESOURCES_RESOURCE_URL = "resources"
LS_RESOURCE_URL = "ls"
COPY_RESOURCE_URL = "cp"


class ResourcesClient(base_client.BaseClient):

    def get_ls(self, path):
        """Get file list from Spell.

        Keyword arguments:
        path -- the path to list the contents of

        Returns:
        a generator for file details
        """
        endpoint = url_path_join(RESOURCES_RESOURCE_URL, self.owner, LS_RESOURCE_URL, *path.split('/'))
        with self.request("get", endpoint, stream=True) as ls_stream:
            self.check_and_raise(ls_stream)
            if ls_stream.encoding is None:
                ls_stream.encoding = 'utf-8'
            for chunk in ls_stream.iter_lines(decode_unicode=True):
                try:
                    chunk = json.loads(chunk, cls=LsLineDecoder)
                except ValueError as e:
                    message = "Error decoding the ls response chunk: {}".format(e)
                    raise JsonDecodeError(msg=message, response=ls_stream, exception=e)
                yield chunk
            link = ls_stream.headers.get("Resource-Link", "")
            if len(link) > 0:
                yield json.loads(link)["resource_link"]

    @contextmanager
    def tar_of_path(self, path):
        """Get a tar of the resource path.

        Keyword arguments:
        source_path -- a single file or directory to extract, relative path (probably starting with runs/)
        """
        endpoint = url_path_join(RESOURCES_RESOURCE_URL, self.owner, COPY_RESOURCE_URL, *path.split('/'))
        headers = {"Accept": "application/x-tar"}
        with self.request("get", endpoint, headers=headers, stream=True) as response:
            self.check_and_raise(response)

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("application/x-tar"):
                raise ClientException("Unsupported Content-Type: '{}'".format(content_type), response)

            with tarfile.open(fileobj=response.raw, mode='r|*') as tar:
                yield tar


class LsLineDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(LsLineDecoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        try:
            return models.LsLine(**obj)
        except TypeError:
            return models.Error.response_dict_to_object(obj)
