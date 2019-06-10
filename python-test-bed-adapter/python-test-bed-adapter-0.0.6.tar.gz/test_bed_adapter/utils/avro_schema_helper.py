import avro.schema
import avro.io
import io
import sys
import json
import logging
import avro.datafile


class AvroSchemaHelper:
    avro_schema: object

    def __init__(self, schema_str, topic, schema_id):
        self._schema_str = schema_str
        self.topic = topic
        self._schema_id = schema_id
        json_schema = json.loads(self._schema_str)
        self.avro_schema = avro.schema.SchemaFromJSONData(json_schema)

    def avro_encode_messages(self, json_messages):
        bytes_writer = io.BytesIO()
        writer = avro.io.DatumWriter(self.avro_schema)
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(json_messages, encoder)
        raw_bytes = bytes_writer.getvalue()
        # Add 5-byte header the first byte is reserved for future, 4 bytes for 32 bit number indicating ID
        return bytes(bytearray(b'\x00') +
                     bytearray(self._schema_id.to_bytes(4, byteorder='big')) +
                     bytearray(raw_bytes))

    def avro_decode_message(self, message):
        if message:
            bytes_from_message = bytearray(message)
            # Check ID for coherency
            message_id = int.from_bytes(bytes_from_message[1:5], byteorder='big')
            if self._schema_id != message_id:
                logging.warning("Possible incoherence between message's id (%d) and schema's id (%d), for topic (%s)",
                                message_id, self._schema_id, self.topic)
            # Remove 5-byte header the first byte is reserved for future, 4 bytes for 32 bit number indicating ID
            message = bytes(bytes_from_message[5:])
            # Parse the rest of the message using the schema
            bytes_reader = io.BytesIO(message)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(self.avro_schema)
            decoded_messages = []

            # We iterate in case there are more than one messages
            while bytes_reader.tell() < len(message):
                try:
                    # Here is where the messages are read
                    decoded_messages.append(reader.read(decoder))
                    sys.stdout.flush()
                except Exception as e:
                    logging.error(e)
            return decoded_messages
