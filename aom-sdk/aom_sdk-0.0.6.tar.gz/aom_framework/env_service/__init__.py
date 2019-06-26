# Copyright 2019 Age of Minds inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module exposes the interfaces needed to implement
an environment service to which the AoM orchestrator connects to."""

from aom_framework.env_service.service_impl import launch_server

import aom_framework.services_pb2 as _service_pbs
import aom_framework.services_pb2_grpc as _service_grpc

from aom_framework.services_pb2_grpc import EnvironmentServicer as Servicer
from aom_framework.services_pb2_grpc import (
    add_EnvironmentServicer_to_server as add_servicer_to_server)

from aom_framework.protocols_pb2 import (
    EnvStartRequest, EnvStartReply, EnvUpdateRequest, EnvUpdateReply)


SERVICE_NAME = _service_pbs.DESCRIPTOR.services_by_name['Environment'].full_name
