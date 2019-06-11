# -*- coding: utf-8 -*-

from benedict.utils import io_util


class IODict(dict):

    def __init__(self, *args, **kwargs):
        super(IODict, self).__init__(*args, **kwargs)

    # @classmethod
    # def from_base64(cls, base64_string):
    #     return io_util.decode_base64(base64_string)

    # @classmethod
    # def from_base64_file(cls, filepath):
    #     return io_util.decode_base64(io_util.read_file(filepath))

    # @classmethod
    # def from_base64_url(cls, url):
    #     return io_util.decode_base64(io_util.read_url(url))

    @classmethod
    def from_json(cls, json_string):
        return io_util.decode_json(json_string)

    @classmethod
    def from_json_file(cls, filepath):
        return io_util.decode_json(io_util.read_file(filepath))

    @classmethod
    def from_json_url(cls, url):
        return io_util.decode_json(io_util.read_url(url))

    # @classmethod
    # def from_query_string(cls, query_string):
    #     return io_util.decode_query_string(query_string)

    # @classmethod
    # def from_xml(cls, xml_string):
    #     return io_util.decode_xml(xml_string)

    # @classmethod
    # def from_xml_file(cls, filepath):
    #     return io_util.decode_xml(io_util.read_file(filepath))

    # @classmethod
    # def from_xml_url(cls, url):
    #     return io_util.decode_xml(io_util.read_url(url))

    # @classmethod
    # def from_yaml(cls, yaml_string):
    #     return io_util.decode_yaml(yaml_string)

    # @classmethod
    # def from_yaml_file(cls, filepath):
    #     return io_util.decode_yaml(io_util.read_file(filepath))

    # @classmethod
    # def from_yaml_url(cls, url):
    #     return io_util.decode_yaml(io_util.read_url(url))

    # @classmethod
    # def to_base64(cls, d, filepath=None):
    #     s = io_util.encode_base64(d)
    #     io_util.write_file(filepath, content=s)
    #     return s

    @classmethod
    def to_json(cls, d, filepath=None):
        s = io_util.encode_json(d)
        if filepath:
            io_util.write_file(filepath, content=s)
        return s

    # @classmethod
    # def to_query_string(cls, d, filepath=None):
    #     s = io_util.encode_query_string(d)
    #     io_util.write_file(filepath, content=s)
    #     return s

    # @classmethod
    # def to_xml(cls, d, filepath=None):
    #     s = io_util.encode_xml(d)
    #     io_util.write_file(filepath, content=s)
    #     return s

    # @classmethod
    # def to_yaml(cls, d, filepath=None):
    #     s = io_util.encode_yaml(d)
    #     io_util.write_file(filepath, content=s)
    #     return s

    # def to_base64(self, filepath=None):
    #     return IODict.to_base64(self, filepath)

    def to_json(self, filepath=None):
        return IODict.to_json(self, filepath)

    # def to_query_string(self, filepath=None):
    #     return IODict.to_query_string(self, filepath)

    # def to_xml(self, filepath=None):
    #     return IODict.to_xml(self, filepath)

    # def to_yaml(self, filepath=None):
    #     return IODict.to_yaml(self, filepath)

