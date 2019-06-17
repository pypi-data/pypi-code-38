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
import copy
import json
from typing import Dict, Union
from urllib.parse import urlparse

from .datasetsclient import build_datasetsclient
from .modelclient import ModelClient
from .modelclient import build_modelclient
from .modelcontext import ModelStatusContextualizer
from .modelprocess import ModelProcess
from .types import InputMessage, Model, ModelEvent
from .types import JSONType
from .utils import get_logger

log = get_logger(__name__)

class ModelRunner:
    """
    Executes the ModelProcessor implementation and stores and retrieves execution artifacts.
    """

    def __init__(self, modelprocess: ModelProcess) -> None:
        self.modelprocess = modelprocess

    ## Public ##

    def run_train(self, context: InputMessage):
        """
        Runs the ModelProcess.train function.

        :param context: A Cortex InputMessage.
        """
        ## TODO: make client api versions configurable (passed via ENV vars or InputMessage?)
        dataset_client = build_datasetsclient(context, 3)
        model_client   = build_modelclient(context, 2)
        model = model_client.create_model_version(context.instance_id,
                                                  context.channel_id,
                                                  self.modelprocess.name,
                                                  self.modelprocess.__doc__ or \
                                                  self.modelprocess.name)

        request_args = self._prepare_request_args(context)
        c = ModelStatusContextualizer(model_client, model, 'cortex.train')
        f = c.contextualize(self.modelprocess.train)
        f(request_args, model, dataset_client, model_client)
        return model._id

    def run_inquire(self, context: InputMessage) -> JSONType:
        """Runs the ModelProcess.inquire function.

        :param context: A Cortex InputMessage
        """
        model_client   = build_modelclient(context, 2)
        ## TODO: the model to load won't always be latest,
        ## and it will be loaded based on a deployment spec
        model = model_client.get_model(context.instance_id,
                                       context.channel_id,
                                       self.modelprocess.name,
                                       'latest')
        request_args = self._prepare_request_args(context)
        self._run_inquire_init(model, model_client)
        return self.modelprocess.inquire(request_args, model, model_client)

    def run_inquire_init(self, context: InputMessage) -> JSONType:
        """
        Downloads the trained model from Cortex and caches it to disk.

        :param context: A Cortex InputMessage.
        :return: Success or error result message.
        """
        model_client   = build_modelclient(context, 2)
        ## TODO: the model to load won't always be latest,
        ## and it will be loaded based on a deployment spec
        model = model_client.get_model(context.instance_id,
                                       context.channel_id,
                                       self.modelprocess.name,
                                       'latest')
        return self._run_inquire_init(model, model_client)

    def _run_inquire_init(self, model, model_client):
        """
        Downloads the trained model from Cortex and caches it to disk.
        """
        ser_model_refs = model_client.get_serialized_model_refs(model._id)
        for k, v in ser_model_refs.items():
            if not model_client.load_state_cache(model, k):
                stream = model_client.download_state(model, k)
                model_client.save_state_cache(model, k, stream)
        return ser_model_refs


    ## Private ##

    @staticmethod
    def _prepare_request_args(input_message: InputMessage) -> Dict[str, object]:
        def hydrate_values(dic: Dict[str, Union[str, bytes, bytearray]]) -> Dict[str, object]:
            ## This is ugly, but Cortex 5 properties can not be nested (JSON),
            ## so they need to be encoded as strings.
            result = {}
            for k, v in dic.items():
                try:
                    result[k] = json.loads(v)
                except (json.decoder.JSONDecodeError, TypeError):
                    result[k] = v
            return result
        payload = input_message.payload.copy()
        properties = input_message.properties.copy()
        result = hydrate_values(properties)
        result.update(payload)
        return result
