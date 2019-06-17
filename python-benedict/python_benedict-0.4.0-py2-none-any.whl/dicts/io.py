# -*- coding: utf-8 -*-

from benedict.utils import io_util


class IODict(dict):

    def __init__(self, *args, **kwargs):
        super(IODict, self).__init__(*args, **kwargs)

    # @staticmethod
    # def from_base64(base64_string):
    #     return io_util.decode_base64(base64_string)

    # @staticmethod
    # def from_base64_file(filepath):
    #     return io_util.decode_base64(io_util.read_file(filepath))

    # @staticmethod
    # def from_base64_url(url):
    #     return io_util.decode_base64(io_util.read_url(url))

    @staticmethod
    def from_json(json_string):
        return io_util.decode_json(json_string)

    @staticmethod
    def from_json_file(cls, filepath):
        return io_util.decode_json(io_util.read_file(filepath))

    @staticmethod
    def from_json_url(url):
        return io_util.decode_json(io_util.read_url(url))

    # @staticmethod
    # def from_query_string(query_string):
    #     return io_util.decode_query_string(query_string)

    # @staticmethod
    # def from_xml(xml_string):
    #     return io_util.decode_xml(xml_string)

    # @staticmethod
    # def from_xml_file(filepath):
    #     return io_util.decode_xml(io_util.read_file(filepath))

    # @staticmethod
    # def from_xml_url(url):
    #     return io_util.decode_xml(io_util.read_url(url))

    # @staticmethod
    # def from_yaml(yaml_string):
    #     return io_util.decode_yaml(yaml_string)

    # @staticmethod
    # def from_yaml_file(filepath):
    #     return io_util.decode_yaml(io_util.read_file(filepath))

    # @staticmethod
    # def from_yaml_url(url):
    #     return io_util.decode_yaml(io_util.read_url(url))

    # def to_base64(self, filepath=None):
    #     return IODict.to_base64(self, filepath)

    def to_json(self):
        return io_util.encode_json(self)

    # def to_query_string(self, filepath=None):
    #     return IODict.to_query_string(self, filepath)

    # def to_xml(self, filepath=None):
    #     return IODict.to_xml(self, filepath)

    # def to_yaml(self, filepath=None):
    #     return IODict.to_yaml(self, filepath)

