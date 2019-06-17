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

import io
from typing import Union

from diskcache import Cache

from .types import Model
from .utils import get_logger

log = get_logger(__name__)


class CacheHandler:

    """
    Provides methods for saving and loading Cortex models and data.
    """
    def __init__(self, path):
        self.cache = Cache(path)

    def save_state(self, model: Model, key: str, data: Union[bytes, io.BufferedReader]):
        """
        Saves a Cortex model and state.
        """
        log.info("Saving state to cache... key: {}".format(key))
        ## NOTE: hacky, what's the best way to check if `data` is file-like?
        #r = self.cache.add(key, data, read=hasattr(data, 'read'))
        r = self.cache.add(key, data, read=True)
        if r:
            log.info("Saved {} to cache".format(key))
        else:
            log.info("{} already in cache. Nothing to do.".format(key))

    def load_state(self, model: Model, key: str) -> Union[bytes, io.BufferedReader]:
        """
        Loads a Cortex model and state.
        """
        print("Loading state from cache... key: {}".format(key))
        result = self.cache.get(key, read=True)
        if result:
            log.info("Loaded {} from cache".format(key))
        else:
            log.info("{} not in cache".format(key))
        return result
