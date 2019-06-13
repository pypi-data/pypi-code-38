"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from datetime import datetime
import io
import json
import os
from typing import Dict, Union
from urllib.parse import urlparse
from requests.packages.urllib3.response import HTTPResponse

from .authenticationclient import AuthenticationClient
from .cache import CacheHandler
from .client import build_client
from .connectionclient import ConnectionClient
from .serviceconnector import ServiceConnector
from .types import InputMessage, ModelEvent, Model
from .utils import get_logger

log = get_logger(__name__)

class ModelClient:
    """
    A client-side representation of a Cortex model.
    """

    URIs = {'models':           'models',
            'model_events':     'models/events',
            'model_versions':   'models/versions',
            'model_serialized': 'models/{}/serialized',
            'content':          'content'}

    def __init__(self, url, version, token, cache_dir='/tmp/cortex-cache'):
        self._serviceconnector = ServiceConnector(url, version, token)
        self.cache = CacheHandler(cache_dir)

    # TODO: should this return a Response or the object creted directly?
    def create_model_version(self, agent_id, processor_id, name, description) -> Model:
        """
        Creates a new Mmdel version to link with a training execution.

        :param agent_id: The unique id of the agent instance.
        :param processor_id: The unique id of the processor.
        :param name: The name of the new model.
        :param description: A description of the model.
        :return: A model object.
        """
        body    = {"agentId": agent_id,
                   "processorId": processor_id,
                   "name": name,
                   "description": description}
        body_s  = json.dumps(body)
        headers = {'Content-Type': 'application/json'}
        response = self._serviceconnector.request('POST', self.URIs['models'], body_s, headers)
        response.raise_for_status()
        return Model._make(response.json())

    ## ModelEvent loggers ##

    def log_data_stats(self, model, value: object):
        """
        Before training, logs stats about the data itself. (sync)

        :param model: The model object against which to log events.
        :param value: A value to log.
        """
        return self.log_event(model, 'cortex.train.data.stats', value)

    def log_hyperparams(self, model, value):
        """
        Logs hyperparameters (sync).

        :param model: The model object against which to log events.
        :param value: A value to log.
        """
        return self.log_event(model, 'cortex.train.hyperparameters', value)

    def log_train_progress(self, model, value: object):
        """
        Logs training progress (sync).

        :param model: The model object against which to log events.
        :param value: The value that represents the progress.
        """
        return self._log_train_status(model, {'progress': value})

    def log_serving_datum(self, model, label: str, value: object):
        """
        Logs inquiry results (sync/async).

        :param model: A model object against which to log events.
        :param label: A label attached to the event key.
        :param value: The value to log.
        """
        return self.log_event(model, 'inquiry.' + label, value)

    def log_event(self, model, key: str, value: object):
        """
        Logs a generic ModelEvent (sync/async).

        :param model: A model object against which to log events.
        :param key: A string specifying the event type (e.g., cortex.train.status).
        :param value: The value to log.
        :return: A response object.
        """
        uri    = self.URIs['model_events']
        body   = ModelEvent(model._id, key, value, str(datetime.now()))
        body_s = json.dumps(body._asdict())
        headers = {'Content-Type': 'application/json'}
        return self._serviceconnector.request('POST', uri, body_s, headers)

    ## Data ##

    def get_model(self, agent_id, processor_id, name, version):
        """
        Gets the Cortex model object.

        :param agent_id: The ID of the agent-instance to which the model belongs.
        :param processor_id: The ID of the processor to which the model belongs.
        :param name: The name of the model to retrieve.
        :param version: The version of the model to retrieve.
        :return: A model object.
        """
        uri = '/'.join([self.URIs['model_versions'], agent_id, processor_id, name, version])
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return Model._make(r.json())

    def get_model_id(self, agent_id, processor_id, name, version):
        """
        Returns the unique ID of a model.
        """
        return self.get_model(agent_id, processor_id, name, version)._id

    def get_serialized_model_refs(self, model_id):
        uri = self.URIs['model_serialized'].format(model_id)
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return r.json()

    ## TODO: What should be the file path in Minio/S3?
    ## (cortex-content) /<tenant>/models/<processorname>/<agent id>/<processor ref id>/<model version>/<filename>
    def upload_state(self, model, key: str, stream: object) -> object:
        """
        Uploads a trained model (sync).

        :param model: The model object associated with the serialized trained model to store.
        :param key: The path where the serialized model is stored.
        :param value: The payload (serialized model) to store.
        :return: The upload state value.
        """
        log.info('Uploading state with key "{}" for model "{}..."'.format(key, model.name))
        client = ConnectionClient(
            self._serviceconnector.url,
            2,
            self._serviceconnector.token
        )
        coord = model._construct_serialized_model_path(key)
        r = client.uploadStreaming(key=coord, content_type='application/octet-stream', stream=stream)
        self._log_serialized_model_refs(model, {key: coord})
        log.info('Uploaded saved.')
        return r

    def download_state(self, model: Model, key: str) -> HTTPResponse:
        """
        Downloads the persisted model.

        :param model: The model object from which to retrieve an artifact (e.g., serialized model).
        :param key: The path / name of the object to retrieve.
        :return: The upload state value.
        """
        client = ConnectionClient(
            self._serviceconnector.url,
            2,
            self._serviceconnector.token
        )
        coord = model._construct_serialized_model_path(key)
        return client.download(coord)

    def save_state(self, model, key: str, stream):
        """
        Saves a trained model (sync).

        :param model: The model object associated with the serialized trained model to store.
        :param key: The path where the serialized model is stored.
        :param value: The payload (serialized model) to store.
        :return: The save state value.
        """
        return self.upload_state(model, key, stream)

    def load_state(self, model: Model, key: str):
        """
        Returns the persisted model.

        :param model: The model object from which to retrieve an artifact (e.g., serialized model).
        :param key: The path / name of the object to retrieve.
        :return: The load state value.
        """
        return self.load_state_cache(model, key) or \
               self.download_state(model, key)


    def save_state_cache(self, model: Model, key: str, stream: Union[bytes, io.BufferedReader]):
        """
        Saves a trained model to disk.

        :param model: The model object associated with the serialized trained model to store.
        :param key: The path where the serialized model is stored.
        :param stream: The serialized model to store.

        """
        key = model._construct_serialized_model_path(key)
        return self.cache.save_state(model, key, stream)

    def load_state_cache(self, model: Model, key: str):
        """
        Reads the persisted model from disk cache.

        :param model: The model object from which to retrieve an artifact (e.g., serialized model).
        :param key: The path/name of the object to retrieve.
        """
        key = model._construct_serialized_model_path(key)
        return self.cache.load_state(model, key)

    ## Private ##

    def _log_serialized_model_refs(self, model: Model, value: Dict[str, str]):
        return self.log_event(model, 'cortex.train.model', value)

    def _log_train_status(self, model, value):
        """
        Logs training status (sync).

        :param model: A model object against which to log events.
        :param value: The value to log
        """
        return self.log_event(model, 'cortex.train.status', value)


def build_modelclient(input_message: InputMessage, version) -> ModelClient:
    """
    A ModelClient constructor function.

    :param input_message: The Cortex InputMessage containing all the constructor parameters.
    :return: ModelClient
    """
    return build_client(ModelClient, input_message, version)
