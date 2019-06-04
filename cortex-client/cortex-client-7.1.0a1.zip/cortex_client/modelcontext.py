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
from contextlib import ContextDecorator
import sys
import traceback

from .modelclient import ModelClient
from .types import Model, ModelEvent
from .utils import json_str

class ModelStatusContextualizer:
    """
    Provides a context for the model during training.
    """
    def __init__(self, modelclient: ModelClient, model: Model, context:str) -> None:
        self.modelclient = modelclient
        self.context     = context
        self.model       = model

    def contextualize(self, func):
        def wrapper(*args, **kwargs):
            #val = {ModelEvent.TRAIN_STATUS['STARTED']: {"args": args, "kwargs": kwargs}}
            val = ModelEvent.TRAIN_STATUS['STARTED']
            self.modelclient.log_event(self.model, self._status_key, json_str(val))
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                ex_type, ex, tb = sys.exc_info()
                val = {ModelEvent.TRAIN_STATUS['FAILED']: traceback.format_exception(ex_type, ex, tb)}
                self.modelclient.log_event(self.model, self._status_key, val)
                raise e
            #val = {ModelEvent.TRAIN_STATUS['COMPLETED']: result}
            val = ModelEvent.TRAIN_STATUS['COMPLETED']
            self.modelclient.log_event(self.model, self._status_key, json_str(val))
            return result
        return wrapper

    ## Private ##

    @property
    def _status_key(self):
        return '.'.join([self.context, 'status'])
