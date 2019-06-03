from nanome.util import IntEnum
from . import _UIBaseSerializer
from .. import _Image
from nanome._internal._util._serializers import _ColorSerializer, _ArraySerializer, _ByteSerializer, _StringSerializer, _TypeSerializer

class _ImageSerializer(_TypeSerializer):
    def __init__(self):
        self.data = _ArraySerializer()
        self.data.set_type(_ByteSerializer())
        self.color = _ColorSerializer()
        self.string = _StringSerializer()

    def version(self):
        return 0

    def name(self):
        return "Image"

    def serialize(self, version, value, context):
        context.write_int(value._content_id)
        context.write_using_serializer(self.string, value._file_path)
        context.write_using_serializer(self.color, value._color)
        context.write_uint(value._scaling_option)
        data = []
        if (value._file_path != ""):
            with open(value._file_path, "rb") as f:
                data = f.read()
        context.write_using_serializer(self.data, data)

    def deserialize(self, version, context):
        value = _Image._create()
        value._content_id = context.read_int()
        value._file_path = context.read_using_serializrt(self.string)
        value._color = context.read_using_serializer(self.color)
        value._scaling_option = context.read_uint()
        context.read_using_serializer(self.data) #skipping data.
        return value

_UIBaseSerializer.register_type("Image", _UIBaseSerializer.ContentType.eimage, _ImageSerializer())
