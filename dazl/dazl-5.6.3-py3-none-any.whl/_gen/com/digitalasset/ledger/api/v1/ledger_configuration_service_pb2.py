# Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: com/digitalasset/ledger/api/v1/ledger_configuration_service.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import trace_context_pb2 as com_dot_digitalasset_dot_ledger_dot_api_dot_v1_dot_trace__context__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='com/digitalasset/ledger/api/v1/ledger_configuration_service.proto',
  package='com.digitalasset.ledger.api.v1',
  syntax='proto3',
  serialized_options=_b('\n\036com.digitalasset.ledger.api.v1B$LedgerConfigurationServiceOuterClass'),
  serialized_pb=_b('\nAcom/digitalasset/ledger/api/v1/ledger_configuration_service.proto\x12\x1e\x63om.digitalasset.ledger.api.v1\x1a\x32\x63om/digitalasset/ledger/api/v1/trace_context.proto\x1a\x1egoogle/protobuf/duration.proto\"x\n\x1dGetLedgerConfigurationRequest\x12\x11\n\tledger_id\x18\x01 \x01(\t\x12\x44\n\rtrace_context\x18\xe8\x07 \x01(\x0b\x32,.com.digitalasset.ledger.api.v1.TraceContext\"s\n\x1eGetLedgerConfigurationResponse\x12Q\n\x14ledger_configuration\x18\x01 \x01(\x0b\x32\x33.com.digitalasset.ledger.api.v1.LedgerConfiguration\"m\n\x13LedgerConfiguration\x12*\n\x07min_ttl\x18\x01 \x01(\x0b\x32\x19.google.protobuf.Duration\x12*\n\x07max_ttl\x18\x02 \x01(\x0b\x32\x19.google.protobuf.Duration2\xb8\x01\n\x1aLedgerConfigurationService\x12\x99\x01\n\x16GetLedgerConfiguration\x12=.com.digitalasset.ledger.api.v1.GetLedgerConfigurationRequest\x1a>.com.digitalasset.ledger.api.v1.GetLedgerConfigurationResponse0\x01\x42\x46\n\x1e\x63om.digitalasset.ledger.api.v1B$LedgerConfigurationServiceOuterClassb\x06proto3')
  ,
  dependencies=[com_dot_digitalasset_dot_ledger_dot_api_dot_v1_dot_trace__context__pb2.DESCRIPTOR,google_dot_protobuf_dot_duration__pb2.DESCRIPTOR,])




_GETLEDGERCONFIGURATIONREQUEST = _descriptor.Descriptor(
  name='GetLedgerConfigurationRequest',
  full_name='com.digitalasset.ledger.api.v1.GetLedgerConfigurationRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ledger_id', full_name='com.digitalasset.ledger.api.v1.GetLedgerConfigurationRequest.ledger_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='trace_context', full_name='com.digitalasset.ledger.api.v1.GetLedgerConfigurationRequest.trace_context', index=1,
      number=1000, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=185,
  serialized_end=305,
)


_GETLEDGERCONFIGURATIONRESPONSE = _descriptor.Descriptor(
  name='GetLedgerConfigurationResponse',
  full_name='com.digitalasset.ledger.api.v1.GetLedgerConfigurationResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ledger_configuration', full_name='com.digitalasset.ledger.api.v1.GetLedgerConfigurationResponse.ledger_configuration', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=307,
  serialized_end=422,
)


_LEDGERCONFIGURATION = _descriptor.Descriptor(
  name='LedgerConfiguration',
  full_name='com.digitalasset.ledger.api.v1.LedgerConfiguration',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='min_ttl', full_name='com.digitalasset.ledger.api.v1.LedgerConfiguration.min_ttl', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_ttl', full_name='com.digitalasset.ledger.api.v1.LedgerConfiguration.max_ttl', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=424,
  serialized_end=533,
)

_GETLEDGERCONFIGURATIONREQUEST.fields_by_name['trace_context'].message_type = com_dot_digitalasset_dot_ledger_dot_api_dot_v1_dot_trace__context__pb2._TRACECONTEXT
_GETLEDGERCONFIGURATIONRESPONSE.fields_by_name['ledger_configuration'].message_type = _LEDGERCONFIGURATION
_LEDGERCONFIGURATION.fields_by_name['min_ttl'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_LEDGERCONFIGURATION.fields_by_name['max_ttl'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
DESCRIPTOR.message_types_by_name['GetLedgerConfigurationRequest'] = _GETLEDGERCONFIGURATIONREQUEST
DESCRIPTOR.message_types_by_name['GetLedgerConfigurationResponse'] = _GETLEDGERCONFIGURATIONRESPONSE
DESCRIPTOR.message_types_by_name['LedgerConfiguration'] = _LEDGERCONFIGURATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GetLedgerConfigurationRequest = _reflection.GeneratedProtocolMessageType('GetLedgerConfigurationRequest', (_message.Message,), dict(
  DESCRIPTOR = _GETLEDGERCONFIGURATIONREQUEST,
  __module__ = 'com.digitalasset.ledger.api.v1.ledger_configuration_service_pb2'
  # @@protoc_insertion_point(class_scope:com.digitalasset.ledger.api.v1.GetLedgerConfigurationRequest)
  ))
_sym_db.RegisterMessage(GetLedgerConfigurationRequest)

GetLedgerConfigurationResponse = _reflection.GeneratedProtocolMessageType('GetLedgerConfigurationResponse', (_message.Message,), dict(
  DESCRIPTOR = _GETLEDGERCONFIGURATIONRESPONSE,
  __module__ = 'com.digitalasset.ledger.api.v1.ledger_configuration_service_pb2'
  # @@protoc_insertion_point(class_scope:com.digitalasset.ledger.api.v1.GetLedgerConfigurationResponse)
  ))
_sym_db.RegisterMessage(GetLedgerConfigurationResponse)

LedgerConfiguration = _reflection.GeneratedProtocolMessageType('LedgerConfiguration', (_message.Message,), dict(
  DESCRIPTOR = _LEDGERCONFIGURATION,
  __module__ = 'com.digitalasset.ledger.api.v1.ledger_configuration_service_pb2'
  # @@protoc_insertion_point(class_scope:com.digitalasset.ledger.api.v1.LedgerConfiguration)
  ))
_sym_db.RegisterMessage(LedgerConfiguration)


DESCRIPTOR._options = None

_LEDGERCONFIGURATIONSERVICE = _descriptor.ServiceDescriptor(
  name='LedgerConfigurationService',
  full_name='com.digitalasset.ledger.api.v1.LedgerConfigurationService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=536,
  serialized_end=720,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetLedgerConfiguration',
    full_name='com.digitalasset.ledger.api.v1.LedgerConfigurationService.GetLedgerConfiguration',
    index=0,
    containing_service=None,
    input_type=_GETLEDGERCONFIGURATIONREQUEST,
    output_type=_GETLEDGERCONFIGURATIONRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_LEDGERCONFIGURATIONSERVICE)

DESCRIPTOR.services_by_name['LedgerConfigurationService'] = _LEDGERCONFIGURATIONSERVICE

# @@protoc_insertion_point(module_scope)
