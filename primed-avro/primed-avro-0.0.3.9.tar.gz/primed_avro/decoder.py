import avro
import fastavro
import struct
import io
import avro.io
from avro import schema as avroschema
import json
import primed_avro.util


MAGIC_BYTE = 0


class SerializerError(Exception):
    pass


class AvroDecoder:
    def __init__(self, schema):
        raise NotImplementedError()
        parsed_schema = avroschema.Parse(json.dumps(schema))
        self._writer = avro.io.DatumWriter(parsed_schema)

    def decode(self, record):
        writer_schema_obj = None  # TODO: where to obtain this?
        reader_schema_obj = None  # TODO: where to obtain this?

        if record is None:
            return None

        if len(record) <= 5:
            raise SerializerError("record is too small to decode")

        avro_reader = avro.io.DatumReader(writer_schema_obj, reader_schema_obj)

        with primed_avro.util.ContextStringIO(record) as payload:
            magic, schema_id = struct.unpack(">bI", payload.read(5))
            if magic != MAGIC_BYTE:
                raise SerializerError("record does not start with magic byte")

            return avro_reader.read(avro.io.BinaryDecoder(payload))


class FastAvroDecoder:
    def __init__(self, schema_registry, schemaless=True):
        self._schema_registry = schema_registry
        self._decoder = fastavro.schemaless_reader if schemaless else fastavro.reader

    def decode(self, record):

        with primed_avro.util.ContextStringIO(record) as buf:
            magic, schema_id = struct.unpack(">bI", buf.read(5))
            if magic != MAGIC_BYTE:
                raise SerializerError("record does not start with magic byte")

            schema = self._schema_registry.get_by_id(schema_id).schema

            return self._decoder(buf, schema)
    
    def decode_with_meta(self, record):

        with primed_avro.util.ContextStringIO(record) as buf:
            magic, schema_id = struct.unpack(">bI", buf.read(5))
            if magic != MAGIC_BYTE:
                raise SerializerError("record does not start with magic byte")

            schema = self._schema_registry.get_by_id(schema_id).schema

            return self._decoder(buf, schema), schema, magic


class Decoder:
    """
    Allows the user to dynamically specify whether to use the
    FastAvro or regular Avro implementations
    """

    _classmap = {"fastavro": FastAvroDecoder, "avro": AvroDecoder}

    def __init__(self, schema, classname="fastavro"):
        self._decoder = Decoder._classmap[classname](schema)

    def get(self):
        return self._decoder
