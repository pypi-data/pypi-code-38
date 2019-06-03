#!/usr/bin/env python

# Copyright 2017 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
from __future__ import absolute_import
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import schema_pb2 as schema__pb2


class SchemaServiceStub(object):
  """Schema services
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetSchema = channel.unary_unary(
        '/schema.SchemaService/GetSchema',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=schema__pb2.Schemas.FromString,
        )


class SchemaServiceServicer(object):
  """Schema services
  """

  def GetSchema(self, request, context):
    """Return active grpc schemas
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_SchemaServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetSchema': grpc.unary_unary_rpc_method_handler(
          servicer.GetSchema,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=schema__pb2.Schemas.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'schema.SchemaService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
