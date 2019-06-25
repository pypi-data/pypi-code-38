# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import copy
import logging

import io

from . import entity_json
from .exceptions import ConfigUploadFailed
from .entitybase import EntityBase
from .pump import Pump
from . import utils

logger = logging.getLogger(__name__)


class Pipe(EntityBase):
    """
    This class represents a pipe.
    """

    def __str__(self):
        result = super().__str__()
        # TODO: add info about task, provider and sink.
        return result

    def get_pump(self):
        url = self._connection.get_pipe_pump_url(self.id)
        response = self._connection.do_get_request(url)
        utils.validate_response_is_ok(response, [200])
        pump_json = response.json()
        return Pump(self, self._connection, pump_json)

    @property
    def source_dataset_id(self):
        """Returns the id of the dataset that this pipe reads data from, or None if the pipe doesn't
        read data from a dataset."""
        effective_config = self._raw_jsondata["config"]["effective"]
        producer_config = effective_config.get("source")
        if producer_config is None:
            return None

        return producer_config.get("dataset")

    @property
    def sink_dataset_id(self):
        """Returns the id of the dataset that this pipe feeds data to, or None if the pipe doesn't
        feed data to a dataset."""
        effective_config = self._raw_jsondata["config"]["effective"]
        sink_config = effective_config.get("sink")
        if sink_config is None:
            return None

        return sink_config.get("dataset")

    @property
    def execution_dataset_id(self):
        """Returns the id of the dataset that this pipe logs to, or None if the pipe doesn't
        log to a dataset (this is the case for the pipes of the old sdshare server and client)."""
        runtime = self._raw_jsondata["runtime"]
        return runtime.get("execution-dataset")

    @property
    def runtime(self):
        return copy.deepcopy(self._raw_jsondata["runtime"])

    def get_entities(self, since=None, limit=None):
        """This returns a generator for iterating over the entities of the source of this pipe.
        :param since:
        :param limit: The maximum number of entities to return. A value of None means return all the entities.
        """
        url = self._connection.get_pipe_entities_url(self.id)

        params = {}
        if since is not None:
            params["since"] = since
        if limit is not None:
            params["limit"] = limit

        # The entities are streamed from the server, so we have to enable streaming here.
        response = self._connection.do_get_request(url, stream=True, params=params)
        utils.validate_response_is_ok(response)

        return entity_json.parse_json_stream(response.raw)

    def post_entities(self, entities,
                      is_full=None,
                      sequence_id=None,
                      request_id=None,
                      previous_request_id=None,
                      is_last=None,
                      is_first=None,
                      ):
        """This posts the specified entities to the pipe. This only works for pipes that has a source
        of the type 'http_endpoint'.
        """
        url = self._connection.get_pipe_receiver_endpoint_url(self.id)

        # If the size of the entities is very large, we have to use chunked encoding; otherwise we will get
        # a "connection reset" error.
        entities_as_json = entity_json.entities_to_json(entities)
        class BytesIOWithNoLength(io.BytesIO):
            def __len__(self):
                raise io.UnsupportedOperation()
            def __bool__(self):
                return True
        entities_stream = BytesIOWithNoLength(entities_as_json.encode("utf-8"))

        params = {}
        if is_full is not None:
            params["is_full"] = True
        if sequence_id is not None:
            params["sequence_id"] = sequence_id
        if request_id is not None:
            params["request_id"] = request_id
        if previous_request_id is not None:
            params["previous_request_id"] = previous_request_id
        if is_last is not None:
            params["is_last"] = is_last
        if is_first is not None:
            params["is_first"] = is_first

        response = self._connection.do_post_request(url,
                                                    headers={"Content-Type": "application/json"},
                                                    params=params,
                                                    data=entities_stream)
        utils.validate_response_is_ok(response)
        return response.json()

    def delete(self):
        """Deletes this pipe from the sesam-node.
        """
        url = self._connection.get_pipe_url(self.id)
        response = self._connection.do_delete_request(url)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)

    def modify(self, pipe_config, force=False):
        """Modifies the pipe with the specified configuration."""
        request_params = {"force": "true" if force else "false"}
        pipe_config = copy.deepcopy(pipe_config)
        response = self._connection.do_put_request(self._connection.get_pipe_config_url(self.id), json=pipe_config,
                                                   params=request_params)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200, 400])

        if response.status_code == 400:
            raise ConfigUploadFailed(response=response)

        self.update_raw_jsondata(response.text)
