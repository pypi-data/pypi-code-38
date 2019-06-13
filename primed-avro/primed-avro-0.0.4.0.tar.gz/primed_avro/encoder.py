import avro
import fastavro
import struct
import io
import avro.io
from avro import schema as avroschema
import json
import primed_avro.util

MAGIC_BYTE = 0


class AvroEncoder:
    def __init__(self, schema, schemaless=True):
        if not schemaless:
            raise Exception("AvroEncoder does not support encoding schema into records")

        parsed_schema = avroschema.Parse(json.dumps(schema))
        self._encoder = avro.io.DatumWriter(parsed_schema)

    def encode(self, schema_id, record):
        # this is the reference implementation made by confluent
        # https://github.com/confluentinc/confluent-kafka-python/blob/master/confluent_kafka/avro/serializer/message_serializer.py#L136
        with primed_avro.util.ContextStringIO() as outf:
            # magic byte
            outf.write(struct.pack("b", MAGIC_BYTE))

            # write the schema ID in network byte order (big end)
            outf.write(struct.pack(">I", schema_id))

            # write the record to the rest of it
            # Create an encoder that we'll write to
            encoder = avro.io.BinaryEncoder(outf)

            self._encoder.write(record, encoder)

            return outf.getvalue()


class FastAvroEncoder:
    def __init__(self, schema, schemaless=True):
        self.parsed_schema = fastavro.parse_schema(schema)
        self._encoder = fastavro.schemaless_writer if schemaless else fastavro.writer

    def encode(self, schema_id, record):
        fastavro.validation.validate(record, self.parsed_schema)

        with primed_avro.util.ContextStringIO() as outf:
            outf.write(bytes([MAGIC_BYTE]))  # magic byte
            outf.write((schema_id).to_bytes(4, byteorder="big"))  # schema id
            self._encoder(outf, self.parsed_schema, record)
            return outf.getvalue()


class Encoder:
    """
    Allows the user to dynamically specify whether to use the
    FastAvro or regular Avro implementations
    """

    _classmap = {"fastavro": FastAvroEncoder, "avro": AvroEncoder}

    def __init__(self, schema, schemaless=True, classname="fastavro"):
        self._encoder = Encoder._classmap[classname](schema, schemaless)

    def get(self):
        return self._encoder
