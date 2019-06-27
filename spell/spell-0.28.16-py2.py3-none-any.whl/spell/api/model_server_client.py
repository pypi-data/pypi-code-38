import json
from spell.api import base_client
from spell.api.utils import url_path_join

from requests.exceptions import ChunkedEncodingError
from spell.api.exceptions import JsonDecodeError

MODEL_SERVER_URL = "model_servers"


class ModelServerClient(base_client.BaseClient):

    def new_model_server(self, server_name, tag, path, type, cluster_id, docker_image=None):
        """Create a new model server.

        Keyword arguments:
        server_name - the name of the model server
        tag - the tag of the model server
        path - path which points to the model
        type - type of model we are serving
        docker_image - docker image to use if overriding default

        Returns:
        a ModelServer object for the created model

        """
        payload = {
            "server_name": server_name,
            "tag": tag,
            "resource_path": path,
            "type": type,
            "cluster_id": cluster_id,
            "docker_image": docker_image
        }
        url = url_path_join(MODEL_SERVER_URL, self.owner)
        r = self.request("post", url, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["model_server"]

    def get_model_servers(self):
        """Get a list of model servers.

        Returns:
        a list of Model Server objects for this user

        """
        url = url_path_join(MODEL_SERVER_URL, self.owner)
        r = self.request("get", url)
        self.check_and_raise(r)
        return self.get_json(r)["model_servers"]

    def get_model_server(self, server_name, tag):
        """Get a info about a model server

        Keyword arguments:
        server_name - name of the model server to retrieve
        tag - tag of the model server to retrieve

        Returns:
        a ModelServer object with the specified name and tag
        """
        specifier = "{}:{}".format(server_name, tag)
        url = url_path_join(MODEL_SERVER_URL, self.owner, specifier)
        r = self.request("get", url)
        self.check_and_raise(r)
        return self.get_json(r)["model_server"]

    def delete_model_server(self, server_name, tag):
        """Removes a model server

        Keyword arguments:
        server_name - name of the model server to remove
        tag - tag of the model server to remove

        """
        specifier = "{}:{}".format(server_name, tag)
        url = url_path_join(MODEL_SERVER_URL, self.owner, specifier)
        r = self.request("delete", url)
        self.check_and_raise(r)

    def start_model_server(self, server_name, tag):
        """Starts a model server

        Keyword arguments:
        server_name - name of the model server to start
        tag - tag of the model server to start

        """
        specifier = "{}:{}".format(server_name, tag)
        url = url_path_join(MODEL_SERVER_URL, self.owner, specifier, "start")
        r = self.request("post", url)
        self.check_and_raise(r)

    def stop_model_server(self, server_name, tag):
        """Stops a model server

        Keyword arguments:
        server_name - name of the model server to stop
        tag - tag of the model server to stop

        """
        specifier = "{}:{}".format(server_name, tag)
        url = url_path_join(MODEL_SERVER_URL, self.owner, specifier, "stop")
        r = self.request("post", url)
        self.check_and_raise(r)

    def update_model_server(self, server_name, tag, path, docker_image=None):
        """Update an existing model server with a new configuration.

        Keyword arguments:
        server_name - the name of the model server
        tag - the tag of the model server
        path - path which points to the model
        docker_image - docker image to use if overriding default

        """
        payload = {
            "resource_path": path,
            "docker_image": docker_image
        }
        specifier = "{}:{}".format(server_name, tag)
        url = url_path_join(MODEL_SERVER_URL, self.owner, specifier)
        r = self.request("put", url, payload=payload)
        self.check_and_raise(r)

    def renew_model_server_token(self, server_name, tag):
        """Renews access token for a model server

        Keyword arguments:
        server_name - name of the model server
        tag - tag of the model server

        Returns:
        a ModelServer object with the renewed access token
        """
        specifier = "{}:{}".format(server_name, tag)
        url = url_path_join(MODEL_SERVER_URL, self.owner, specifier, "renew-token")
        r = self.request("post", url)
        self.check_and_raise(r)
        return self.get_json(r)["model_server"]

    def get_model_server_log_entries(self, server_name, tag, follow):
        """Get log entries for a model server

        Keyword arguments:
        server_name - name of the model server
        tag - tag of the model server
        follow -- true if the logs should be followed

        Returns:
        a generator for entries of model sever logs
        """
        specifier = "{}:{}".format(server_name, tag)
        url = url_path_join(MODEL_SERVER_URL, self.owner, specifier, "logs")
        params = {}
        if follow:
            params["follow"] = follow
        with self.request("get", url, params=params, stream=True) as log_stream:
            self.check_and_raise(log_stream)
            try:
                if log_stream.encoding is None:
                    log_stream.encoding = 'utf-8'
                for chunk in log_stream.iter_lines(decode_unicode=True):
                    try:
                        chunk = json.loads(chunk, cls=base_client.SpellDecoder)
                    except ValueError as e:
                        message = "Error decoding the model server log response chunk: {}".format(e)
                        raise JsonDecodeError(msg=message, response=log_stream, exception=e)
                    logEntry = chunk.get("model_server_log_entry")
                    if logEntry:
                        yield logEntry
            except ChunkedEncodingError:
                return
