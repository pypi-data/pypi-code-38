# Copyright 2018 Catalyst IT Ltd.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from rt_client.v2 import client as client_v2
from rt_client import exceptions


_CLIENTS = {"2.0": client_v2.Client, "2": client_v2.Client, "v2": client_v2.Client}


def Client(version="2", *args, **kwargs):
    try:
        return _CLIENTS[str(version).lower()](*args, **kwargs)
    except KeyError:
        raise exceptions.RTClientAPIVersionNotFound(str(version).lower())
