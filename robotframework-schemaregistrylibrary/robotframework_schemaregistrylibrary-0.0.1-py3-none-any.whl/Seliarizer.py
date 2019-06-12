import io
import struct
import avro.io

MAGIC_BYTE = 0

class ContextBytesIO(io.BytesIO):
    ''' Allow use ContextBytesIO with "with" statement '''
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False

class MessageSerializer(object):
    ''' Class allow to encode / decode messages '''

    def __init__(self, client):
        self.client = client
        self.id_to_decoder_func = { }
        self.id_to_writers = { }

    def _set_subject(self, subject):
        subject_suffix = '-value'
        if (subject.endswith("-value")):
            subject = subject
        else:
            subject= subject + subject_suffix
        return subject

    def encode_record_for_topic(self, topic, record):
        if not isinstance(record, dict):
            print ("record must be a dictionary")
            return

        subject = self._set_subject(topic)

        schema_id, schema, version = self.client.get_latest_schema(subject)
        return self.encode_record_with_schema_id(schema_id, schema, record)

    def encode_record_with_schema_id(self, schema_id, schema, record):
        if not isinstance(record, dict):
            print ("record must be a dictionary")
            return

        schema = self.client.get_by_id(schema_id)
        self.id_to_writers[schema_id] = avro.io.DatumWriter(schema)
        with ContextBytesIO() as outf:
            # magic byte
            outf.write(struct.pack('b', MAGIC_BYTE))
            # write the schema ID
            outf.write(struct.pack('>I', schema_id))
            writer = avro.io.DatumWriter(schema)

            encoder = avro.io.BinaryEncoder(outf)
            writer.write(record, encoder)
            return outf.getvalue()

    def get_schema(self, schema_id):
        schema = self.client.get_by_id(schema_id)
        return schema

    def _get_decoder_func(self, schema_id, payload):
        if schema_id in self.id_to_decoder_func:
            return self.id_to_decoder_func[schema_id]

        schema = self.get_schema(schema_id)
        curr_pos = payload.tell()
        avro_reader = avro.io.DatumReader(schema)

        def decoder(p):
            bin_decoder = avro.io.BinaryDecoder(p)
            return avro_reader.read(bin_decoder)

        self.id_to_decoder_func[schema_id] = decoder
        return self.id_to_decoder_func[schema_id]

    def decode_message(self, message):
        if len(message) <= 5:
            print("message is too small to decode")

        with ContextBytesIO(message) as payload:
            magic, schema_id = struct.unpack('>bI', payload.read(5))
            if magic != MAGIC_BYTE:
                print("message does not start with magic byte")
            decoder_func = self._get_decoder_func(schema_id, payload)
            return decoder_func(payload)
