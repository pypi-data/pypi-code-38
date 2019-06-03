# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: animalai/communicator_objects/arena_parameters_proto.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='animalai/communicator_objects/arena_parameters_proto.proto',
  package='communicator_objects',
  syntax='proto3',
  serialized_options=_b('\252\002\034MLAgents.CommunicatorObjects'),
  serialized_pb=_b('\n:animalai/communicator_objects/arena_parameters_proto.proto\x12\x14\x63ommunicator_objects\"\xcf\x03\n\x14\x41renaParametersProto\x12\t\n\x01t\x18\x01 \x01(\x05\x12\x46\n\x05items\x18\x02 \x03(\x0b\x32\x37.communicator_objects.ArenaParametersProto.ItemsToSpawn\x12\x11\n\tblackouts\x18\x03 \x03(\x05\x1a\xd0\x02\n\x0cItemsToSpawn\x12\x0c\n\x04name\x18\x01 \x01(\t\x12R\n\tpositions\x18\x03 \x03(\x0b\x32?.communicator_objects.ArenaParametersProto.ItemsToSpawn.Vector3\x12\x11\n\trotations\x18\x04 \x03(\x02\x12N\n\x05sizes\x18\x05 \x03(\x0b\x32?.communicator_objects.ArenaParametersProto.ItemsToSpawn.Vector3\x12O\n\x06\x63olors\x18\x06 \x03(\x0b\x32?.communicator_objects.ArenaParametersProto.ItemsToSpawn.Vector3\x1a*\n\x07Vector3\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\x12\t\n\x01z\x18\x03 \x01(\x02\x42\x1f\xaa\x02\x1cMLAgents.CommunicatorObjectsb\x06proto3')
)




_ARENAPARAMETERSPROTO_ITEMSTOSPAWN_VECTOR3 = _descriptor.Descriptor(
  name='Vector3',
  full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.Vector3',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='x', full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.Vector3.x', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='y', full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.Vector3.y', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='z', full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.Vector3.z', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=506,
  serialized_end=548,
)

_ARENAPARAMETERSPROTO_ITEMSTOSPAWN = _descriptor.Descriptor(
  name='ItemsToSpawn',
  full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='positions', full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.positions', index=1,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='rotations', full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.rotations', index=2,
      number=4, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sizes', full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.sizes', index=3,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='colors', full_name='communicator_objects.ArenaParametersProto.ItemsToSpawn.colors', index=4,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_ARENAPARAMETERSPROTO_ITEMSTOSPAWN_VECTOR3, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=212,
  serialized_end=548,
)

_ARENAPARAMETERSPROTO = _descriptor.Descriptor(
  name='ArenaParametersProto',
  full_name='communicator_objects.ArenaParametersProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='t', full_name='communicator_objects.ArenaParametersProto.t', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='items', full_name='communicator_objects.ArenaParametersProto.items', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='blackouts', full_name='communicator_objects.ArenaParametersProto.blackouts', index=2,
      number=3, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_ARENAPARAMETERSPROTO_ITEMSTOSPAWN, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=85,
  serialized_end=548,
)

_ARENAPARAMETERSPROTO_ITEMSTOSPAWN_VECTOR3.containing_type = _ARENAPARAMETERSPROTO_ITEMSTOSPAWN
_ARENAPARAMETERSPROTO_ITEMSTOSPAWN.fields_by_name['positions'].message_type = _ARENAPARAMETERSPROTO_ITEMSTOSPAWN_VECTOR3
_ARENAPARAMETERSPROTO_ITEMSTOSPAWN.fields_by_name['sizes'].message_type = _ARENAPARAMETERSPROTO_ITEMSTOSPAWN_VECTOR3
_ARENAPARAMETERSPROTO_ITEMSTOSPAWN.fields_by_name['colors'].message_type = _ARENAPARAMETERSPROTO_ITEMSTOSPAWN_VECTOR3
_ARENAPARAMETERSPROTO_ITEMSTOSPAWN.containing_type = _ARENAPARAMETERSPROTO
_ARENAPARAMETERSPROTO.fields_by_name['items'].message_type = _ARENAPARAMETERSPROTO_ITEMSTOSPAWN
DESCRIPTOR.message_types_by_name['ArenaParametersProto'] = _ARENAPARAMETERSPROTO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ArenaParametersProto = _reflection.GeneratedProtocolMessageType('ArenaParametersProto', (_message.Message,), {

  'ItemsToSpawn' : _reflection.GeneratedProtocolMessageType('ItemsToSpawn', (_message.Message,), {

    'Vector3' : _reflection.GeneratedProtocolMessageType('Vector3', (_message.Message,), {
      'DESCRIPTOR' : _ARENAPARAMETERSPROTO_ITEMSTOSPAWN_VECTOR3,
      '__module__' : 'animalai.communicator_objects.arena_parameters_proto_pb2'
      # @@protoc_insertion_point(class_scope:communicator_objects.ArenaParametersProto.ItemsToSpawn.Vector3)
      })
    ,
    'DESCRIPTOR' : _ARENAPARAMETERSPROTO_ITEMSTOSPAWN,
    '__module__' : 'animalai.communicator_objects.arena_parameters_proto_pb2'
    # @@protoc_insertion_point(class_scope:communicator_objects.ArenaParametersProto.ItemsToSpawn)
    })
  ,
  'DESCRIPTOR' : _ARENAPARAMETERSPROTO,
  '__module__' : 'animalai.communicator_objects.arena_parameters_proto_pb2'
  # @@protoc_insertion_point(class_scope:communicator_objects.ArenaParametersProto)
  })
_sym_db.RegisterMessage(ArenaParametersProto)
_sym_db.RegisterMessage(ArenaParametersProto.ItemsToSpawn)
_sym_db.RegisterMessage(ArenaParametersProto.ItemsToSpawn.Vector3)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
