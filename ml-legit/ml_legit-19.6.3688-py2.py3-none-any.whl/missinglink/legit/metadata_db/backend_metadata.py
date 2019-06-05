# -*- coding: utf-8 -*-
import io
import json
import logging
import os
import sys
import requests
import six
from missinglink.core import ApiCaller
from missinglink.core.api import default_api_retry
from missinglink.core.exceptions import NonRetryException

from ..path_utils import safe_make_dirs
from ..backend_mixin import BackendMixin
from .base_metadata_db import BaseMetadataDB, MetadataOperationError
from six.moves.urllib.parse import urlencode


class WrapUnicodePy2(object):
    def __init__(self, fp):
        self.__fp = fp

    def write(self, s):
        return self.__fp.write(s)

    def seek_to_beginning(self):
        return self.__fp.seek(0)


class WrapUnicodePy3(object):
    def __init__(self, fp):
        self.__fp = fp

    def write(self, s):
        return self.__fp.write(s.encode('utf8'))

    def seek_to_beginning(self):
        return self.__fp.seek(0)


class _StreamArray(list):
    def __init__(self, total_rows):
        super(_StreamArray, self).__init__()
        self._stream = None
        self._total_rows = total_rows

    def __iter__(self):
        return self._csv_enum(self._stream)

    # according to the comment below
    def __len__(self):
        return self._total_rows

    @classmethod
    def _csv_enum(cls, stream):
        import csv

        reader = csv.DictReader(stream)
        replace_names = {'_sha': 'path', '_hash': 'id', '_commit_sha': 'version'}
        for row in reader:
            row_params = {}
            meta = {}
            for key, val in row.items():
                if val == '':
                    continue

                is_meta = key.startswith('_')
                if is_meta:
                    key = replace_names.get(key, key[1:])
                    row_params[key] = val
                    continue

                meta[key] = val

            if meta:
                row_params['meta'] = meta

            yield row_params


class _StreamArrayFromUrl(_StreamArray):
    def __init__(self, total_rows, result_url):
        super(_StreamArrayFromUrl, self).__init__(total_rows)
        r = requests.get(result_url, stream=True)  # allowed to use requests

        if r.encoding is None:
            r.encoding = 'utf-8'

        self._stream = r.iter_lines(decode_unicode=True)


class _CachedSessionWrapper(object):
    def __init__(self, session, cache_folder_full_path):
        from requests_cache import CachedSession

        self.__session = session
        self._first_request = None
        self._is_live_result = True
        self.__cached_session = CachedSession(cache_folder_full_path)  # used as utility to store requests
        self.__wrap_cached_session_send(self.__session)

    @property
    def is_live_result(self):
        return self._is_live_result

    @classmethod
    def convert_result_to_response(cls, result_url, total_rows, total_size, explicit_query, schema):
        data_points = _StreamArrayFromUrl(total_rows, result_url) if total_rows > 0 else []

        response_data = {
            'ok': True,
            'total_data_points': total_rows,
            'total_size': total_size,
            'explicit_query': explicit_query,
            'schema': schema,
            'data_points': data_points,
        }

        return cls.convert_result_to_response_from_data(response_data)

    @classmethod
    def convert_result_to_response_from_data(cls, response_data):
        raw_bytes = io.BytesIO()
        wrap_unicode_class = WrapUnicodePy2 if six.PY2 else WrapUnicodePy3
        raw_string = wrap_unicode_class(raw_bytes)
        json.dump(response_data, raw_string)
        raw_string.seek_to_beginning()

        response = requests.Response()
        response.raw = raw_bytes
        response.status_code = 200

        return response

    def store_response(self, response):
        cache_key = self.__cached_session.cache.create_key(self._first_request)
        response.request = self._first_request
        self.__store_response(cache_key, response)

    def __store_response(self, cache_key, response):
        def should_ignore_exception(exception):
            from sqlite3 import OperationalError

            exc_message = str(exception)
            return isinstance(exception, OperationalError) and exc_message == 'database is locked'

        try:
            self.__cached_session.cache.save_response(cache_key, response)
        except Exception as ex:
            if should_ignore_exception(ex):
                logging.info('Ignoring metadata store_response %s: %s', type(ex), str(ex))
                return
            six.reraise(*sys.exc_info())

    # the first request is the "real" requests (the next are async response check)
    # we store only the first request, check if there is a cached response attached to it
    # in case there is a cached response we send using the cached session class in case it needs to further
    # handle the cache entry
    def __handle_first_request(self, request):
        if self._first_request is not None:
            return None

        self._first_request = request

        cache_key = self.__cached_session.cache.create_key(self._first_request)

        response, timestamp = self.__cached_session.cache.get_response_and_time(cache_key)

        if response is not None:
            self._is_live_result = False

        return response

    def __wrap_cached_session_send(self, session):
        prev_session_send = session.send

        def wrapped_send(request, **kwargs):
            session.send = prev_session_send
            response = self.__handle_first_request(request)
            if response is not None:
                return response

            return prev_session_send(request, **kwargs)

        session.send = wrapped_send


class BackendMetadataDB(BackendMixin, BaseMetadataDB):
    max_query_retry = 3
    default_cache_file_name = 'missinglink_query_v' + str(sys.version_info[0])

    def __init__(self, connection, config, session, cache_folder=None):

        super(BackendMetadataDB, self).__init__(connection, config, session)
        self.__query_parser = None

        if cache_folder is None:
            cache_folder = os.environ.get('ML_CACHE_FOLDER', './ml_cache')

        safe_make_dirs(cache_folder)

        self.__cache_folder_full_path = os.path.join(cache_folder, self.default_cache_file_name)

    @property
    def _query_parser(self):
        from ..scam import QueryParser

        if self.__query_parser is not None:
            return self.__query_parser

        self.__query_parser = QueryParser()

        return self.__query_parser

    def _create_table(self):
        pass

    def _add_missing_columns(self, data_object):
        pass

    def get_data_for_commit(self, sha, commit_sha):
        raise NotImplementedError(self.get_data_for_commit)

    def _add_data(self, data):
        pass

    def add_data_using_url(self, metadata_url, isolation_token):
        if not metadata_url:
            logging.debug('no data provided')
            return

        logging.debug('add data %s', metadata_url)

        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/metadata/head/add' % self._volume_id

            msg = {
                'metadata_url': metadata_url,
                'isolation_token': isolation_token,
            }

            return ApiCaller.call(self._config, session, 'post', url, msg, retry=default_api_retry(), is_async=True)

    @classmethod
    def _convert_type(cls, schema, field_name, field_val):
        schema = schema or {}

        def convert_bool(v):
            return v not in ['no', 'No', 'False', 'false', '0', 0]

        def safe_json_loads(val):
            try:
                return json.loads(val)
            except ValueError:
                return val

        field_convert = {
            'STRING': lambda val: val,
            'JSON': safe_json_loads,
            'INTEGER': int,
            'FLOAT': float,
            'BOOLEAN': convert_bool,
        }

        json_complex_field_suffix = '_json'

        if field_name.endswith(json_complex_field_suffix):
            field_name = field_name[:-len(json_complex_field_suffix)]
            field_type = 'JSON'
        else:
            field_type = schema.get(field_name, 'STRING')

        return field_name, field_convert[field_type](field_val)

    @classmethod
    def _create_iter_data(cls, result, schema=None):
        def handle_meta_item():
            def iter_list():
                for meta_key_val in val:
                    yield meta_key_val['key'], meta_key_val.get('val')

            items_iter = val.items if isinstance(val, dict) else iter_list

            meta = [cls._convert_type(schema, k, v) for k, v in items_iter()]

            return dict(meta)

        for data_point in result.get('data_points') or []:
            result_data_point = {}

            for key, val in data_point.items():
                if key == 'meta':
                    result_data_point['meta'] = handle_meta_item()
                    continue

                key, val = cls._convert_type(schema, '@' + key, val)
                result_data_point[key] = val

            yield result_data_point

    def __is_stable_query(self, query_text):
        from ..scam import QueryUtils

        return QueryUtils.get_version(query_text, parser_=self._query_parser) not in ['head', 'staging', None]

    @classmethod
    def _schema_as_dict(cls, schema_as_list):
        if schema_as_list is None:
            return None

        if isinstance(schema_as_list, dict):
            return schema_as_list

        if isinstance(schema_as_list, list):
            return {s['name']: s['type'] for s in schema_as_list}

    def query(self, query_text, **kwargs):
        version_query = query_text if query_text else '@version:head'

        is_async = kwargs.pop('is_async', False)

        is_stable_version = self.__is_stable_query(version_query)

        if is_stable_version:
            session_wrapper = _CachedSessionWrapper(self._session, self.__cache_folder_full_path)
        else:
            logging.info('not a stable query, caching cannot be used')
            session_wrapper = None

        params = {
            'query': version_query
        }

        for key, val in kwargs.items():
            if val is None:
                continue

            params[key] = val

        url = 'data_volumes/%s/query/?%s' % (self._volume_id, urlencode(params))

        ctx = {}

        def on_response_create(c):
            def on_response(r):
                c['response'] = r

            return on_response

        try:
            result = ApiCaller.call(
                self._config, self._session, 'get', url,
                retry=default_api_retry(stop_max_attempt_number=self.max_query_retry),
                is_async=is_async, on_response=on_response_create(ctx))
        except NonRetryException as ex:
            msg = 'Failed to run query "%s"\n%s' % (version_query, ex)
            raise NonRetryException(msg)

        # Tuple results always come without schema data, it is called by old clients
        # new clients calls using return_schema=True and the result will be returned using a dict
        if isinstance(result, (tuple, list)):
            result_url, total_rows, total_size, explicit_query = result

            result = {
                'ok': True,
                'result_url': result_url,
                'total_data_points': total_rows,
                'total_size': total_size,
                'explicit_query': explicit_query,
            }

        if not result['ok']:
            raise MetadataOperationError(result['error'])

        is_live_response = session_wrapper and session_wrapper.is_live_result  # response comes from a real server and not cached
        if 'result_url' in result:
            sync_response_from_async = _CachedSessionWrapper.convert_result_to_response(result['result_url'], result['total_data_points'], result['total_size'], result['explicit_query'], result.get('schema'))

            result = sync_response_from_async.json()

            ctx['response'] = sync_response_from_async

        if is_live_response:
            response = ctx['response']
            session_wrapper.store_response(response)

        schema = self._schema_as_dict(result.get('schema'))

        return self._create_iter_data(result, schema), int(result.get('total_data_points', 0)), int(result.get('total_size', 0))

    def _query(self, sql_vars, select_fields, where, **kwargs):
        raise NotImplementedError(self._query)

    def get_all_data(self, sha):
        raise NotImplementedError(self.get_all_data)

    def end_commit(self):
        raise NotImplementedError(self.end_commit)

    def begin_commit(self, commit_sha, tree_id, ts):
        raise NotImplementedError(self.begin_commit)
