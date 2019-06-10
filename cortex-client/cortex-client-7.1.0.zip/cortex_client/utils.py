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
import base64
import json
import logging
from pathlib import Path


def get_cortex_profile(profile_name=None):
    """
    Gets the current cortex profile or the profile that matches the optionaly given name.
    """
    cortex_config_path = Path.home() / '.cortex/config'

    if cortex_config_path.exists():
        with cortex_config_path.open() as f:
            cortex_config = json.load(f)

        if profile_name is None:
            profile_name = cortex_config.get('currentProfile')

        return cortex_config.get('profiles', {}).get(profile_name, {})
    return {}


def get_logger(name):
    """
    Gets a logger with the given name.
    """
    log = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s/%(module)s: %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log


def json_str(val):
    """
    Get the string representation of a json object.
    """
    try:
        return json.dumps(val)
    except TypeError:
        return str(val)


def base64decode_jsonstring(base64encoded_jsonstring:str):
    """
    Loads a json from a base64 encoded json string.
    :param base64encoded_jsonstring:
    :return:
    """
    return json.loads(base64.urlsafe_b64decode(base64encoded_jsonstring).decode('utf-8'))