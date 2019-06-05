# -*- coding: utf-8 -*-
import json
import os
from .path_utils import has_moniker, expend_and_validate_path


class MetadataJsonFile(object):
    @classmethod
    def validate_json_file(cls, metadata_json_file):
        from .data_sync import InvalidJsonFile

        metadata_json_file = expend_and_validate_path(metadata_json_file)

        with open(metadata_json_file) as metadata_file:
            try:
                data = json.load(metadata_file)
            except ValueError as ex:
                raise InvalidJsonFile(metadata_json_file, ex)

        return data


class MetadataFiles(object):
    metadata_ext = '.metadata.json'
    reserved_keywords = ['_id', '_hash', '_sha', '_url', '_commit_sha', '_ts']

    @classmethod
    def __is_meta_folder_file_name(cls, metadata_file_name):
        return os.path.basename(metadata_file_name).lower() == 'folder' + cls.metadata_ext

    @classmethod
    def convert_data_unsupported_type(cls, data):
        from .data_sync import InvalidMetadataException

        result = {}
        for key, val in data.items():
            if key in cls.reserved_keywords:
                raise InvalidMetadataException('Invalid metadata field "%s", field name is reserved' % key)

            if isinstance(val, (dict, list, tuple)):  # we convert arrays and dicts into string as we don't support them yet
                val = json.dumps(val)
                key += '_json'

            result[key] = val

        return result

    @classmethod
    def __handle_json_file(cls, metadata_json_file, on_data):
        data = MetadataJsonFile.validate_json_file(metadata_json_file)

        return on_data(data)

    @classmethod
    def __exract_metadata_path(cls, path):
        return path[:-len(cls.metadata_ext)]

    @classmethod
    def __get_metadata_info(cls, data_path, rel_metadata_file_name):
        full_path_metadata = os.path.join(data_path, rel_metadata_file_name)

        rel_path_key = cls.__exract_metadata_path(rel_metadata_file_name)

        def handle_data(data):
            processed_data = cls.convert_data_unsupported_type(data)

            return rel_path_key, processed_data

        return cls.__handle_json_file(full_path_metadata, handle_data)

    @classmethod
    def __get_folder_metadata_info(cls, data_path, rel_metadata_file_name):
        full_path_metadata = os.path.join(data_path, rel_metadata_file_name)

        rel_path = os.path.relpath(os.path.dirname(full_path_metadata), data_path)

        if rel_path == '.':
            rel_path = ''

        def handle_data(all_files_data):
            for filename, file_data in all_files_data.items():
                processed_file_data = cls.convert_data_unsupported_type(file_data)
                rel_path_key = os.path.join(rel_path, filename)

                yield rel_path_key, processed_file_data

        return cls.__handle_json_file(full_path_metadata, handle_data)

    @classmethod
    def get_metadata(cls, data_path, metadata_rel_file_name):
        # we don't support meta in direct bucket scans
        if has_moniker(data_path):
            yield cls.__exract_metadata_path(metadata_rel_file_name), {}
            return

        if cls.__is_meta_folder_file_name(metadata_rel_file_name):
            for rel_path_key, data in cls.__get_folder_metadata_info(data_path, metadata_rel_file_name):
                yield rel_path_key, data
        else:
            rel_path_key, data = cls.__get_metadata_info(data_path, metadata_rel_file_name)

            yield rel_path_key, data
