import json
import mimetypes
import os
from urllib.parse import urljoin
import requests
from multiprocessing import Lock
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from egcg_core.config import cfg
from egcg_core.app_logging import AppLogger
from egcg_core.exceptions import RestCommunicationError
from egcg_core.util import check_if_nested


class Communicator(AppLogger):
    successful_statuses = (200, 201, 202, 204)

    def __init__(self, auth=None, baseurl=None, retries=5):
        self._baseurl = baseurl
        self._auth = auth
        self.retries = retries
        self._sessions = {}
        self.lock = Lock()

    def begin_session(self):
        s = requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(self.retries, self.retries, self.retries, backoff_factor=0.2))
        s.mount('http://', adapter)
        s.mount('https://', adapter)

        if isinstance(self.auth, tuple):
            s.auth = self.auth
        elif isinstance(self.auth, str):
            s.headers.update({'Authorization': 'Token %s' % self.auth})

        return s

    @property
    def session(self):
        """Create and return a session per PID so each sub-processes will use their own session"""
        pid = os.getpid()
        if pid not in self._sessions:
            self._sessions[pid] = self.begin_session()
        return self._sessions[pid]

    @staticmethod
    def serialise(queries):
        serialised_queries = {}
        for k, v in queries.items():
            serialised_queries[k] = json.dumps(v) if isinstance(v, dict) else v
        return serialised_queries

    @staticmethod
    def get_file_content(file_name):
        """
        Open a file in binary mode and close it afterwards.
        :param str file_name:
        :return: file content
        """
        with open(file_name, 'rb') as f:
            fc = f.read()
        return fc

    @staticmethod
    def _extract_files(json_dict):
        """
        Take a json dict and search all values for a tuple['file',<file_path>]. Extract file_path, read its content and
        create another tuple ready to be used by requests. Also modify the original json input to remove the file entry.
        :param dict json_dict:
        :return: a dict of: {field to update: (filename, file content, file MIME type)}
        """
        files = {}
        for k in json_dict:
            if isinstance(json_dict[k], tuple) and len(json_dict[k]) > 1 and json_dict[k][0] == 'file':
                # Construct the 3 parts file upload tuple as requests requires it
                files[k] = (
                    json_dict[k][1],                                 # file name
                    Communicator.get_file_content(json_dict[k][1]),  # file content
                    mimetypes.guess_type(json_dict[k][1])[0]         # file mime type
                )
        if files:
            # remove the extracted files from the original json
            for f in files:
                json_dict.pop(f)
            return files
        return None

    @staticmethod
    def _detect_files_in_json(json_data):
        if isinstance(json_data, list):
            # Assume a list of dicts
            list_files = []
            list_jsons = []
            for d in json_data:
                _d = dict(d)
                list_files.append(Communicator._extract_files(_d))
                list_jsons.append(_d)
            return list_files, list_jsons
        if isinstance(json_data, dict):
            # Assume a single dict
            _json_dict = dict(json_data)
            return Communicator._extract_files(_json_dict), _json_dict

    @property
    def baseurl(self):
        if self._baseurl is None:
            self._baseurl = cfg['rest_api']['url'].rstrip('/')
        return self._baseurl

    @property
    def auth(self):
        if self._auth is None and 'username' in cfg['rest_api'] and 'password' in cfg['rest_api']:
            self._auth = (cfg['rest_api']['username'], cfg['rest_api']['password'])
        return self._auth

    def api_url(self, endpoint):
        return '{base_url}/{endpoint}/'.format(base_url=self.baseurl, endpoint=endpoint)

    @staticmethod
    def _parse_query_string(query_string, requires=None):
        if '?' not in query_string:
            return {}

        if query_string.count('?') != 1:
            raise RestCommunicationError('Bad query string: ' + query_string)

        href, query = query_string.split('?')
        query = dict(x.split('=') for x in query.split('&'))
        if requires and not all(r in query for r in requires):
            raise RestCommunicationError('%s did not contain all required fields: %s' % (query_string, requires))
        return query

    def _req(self, method, url, quiet=False, **kwargs):
        # can't upload json and files at the same time, so we need to move the json parameter to data
        # data can't upload complex structures that would require json encoding.
        # this means we can't upload data with nested lists/dicts at the same time as files
        if kwargs.get('files') and kwargs.get('json'):
            if check_if_nested(kwargs.get('json')):
                raise RestCommunicationError('Cannot upload files and nested json in one query')
            kwargs['data'] = kwargs.pop('json')

        self.lock.acquire()
        try:
            r = self.session.request(method, url, **kwargs)
        finally:
            self.lock.release()

        kwargs.pop('files', None)
        # e.g: 'POST <url> ({"some": "args"}) -> {"some": "content"}. Status code 201. Reason: CREATED
        report = '%s %s (%s) -> %s. Status code %s. Reason: %s' % (
            r.request.method, r.request.path_url, kwargs, r.content.decode('utf-8'), r.status_code, r.reason
        )
        if r.status_code in self.successful_statuses:
            if not quiet:
                self.debug(report)
            return r
        else:
            self.error(report)
            raise RestCommunicationError('Encountered a %s status code: %s' % (r.status_code, r.reason))

    def get_content(self, endpoint, paginate=True, quiet=False, **query_args):
        if paginate:
            query_args['max_results'] = query_args.pop('max_results', 100)  # default to page size of 100
            query_args['page'] = query_args.pop('page', 1)

        url = self.api_url(endpoint)
        return self._req('GET', url, quiet=quiet, params=self.serialise(query_args)).json()

    def get_documents(self, endpoint, paginate=True, all_pages=False, quiet=False, **query_args):
        content = self.get_content(endpoint, paginate, quiet, **query_args)
        elements = content['data']

        if all_pages:
            while 'next' in content['_links']:
                next_query = self._parse_query_string(content['_links']['next']['href'], requires=('max_results', 'page'))
                query_args.update(next_query)
                content = self.get_content(endpoint, paginate, quiet, **query_args)
                elements.extend(content['data'])

        return elements

    def get_document(self, endpoint, idx=0, **query_args):
        documents = self.get_documents(endpoint, **query_args)
        if documents:
            return documents[idx]
        else:
            self.warning('No document found in endpoint %s for %s', endpoint, query_args)

    def post_entry(self, endpoint, payload, use_data=False):
        files, payload = self._detect_files_in_json(payload)
        if use_data:
            return self._req('POST', self.api_url(endpoint), data=payload, files=files)
        else:
            return self._req('POST', self.api_url(endpoint), json=payload, files=files)

    def put_entry(self, endpoint, element_id, payload):
        files, payload = self._detect_files_in_json(payload)
        return self._req('PUT', urljoin(self.api_url(endpoint), element_id), json=payload, files=files)

    def _patch_entry(self, endpoint, doc, payload, update_lists=None):
        """
        Patch a specific database item (specified by doc) with the given data payload.
        :param str endpoint:
        :param dict doc: The entry in the database to patch (contains the relevant _id and _etag)
        :param dict payload: Data with which to patch doc
        :param list update_lists: Doc items listed here will be appended rather than replaced by the patch
        """
        url = urljoin(self.api_url(endpoint), doc['_id'])
        files, payload = self._detect_files_in_json(payload)
        _payload = dict(payload)
        if update_lists:
            for l in update_lists:
                content = doc.get(l, [])
                new_content = [x for x in _payload.get(l, []) if x not in content]
                _payload[l] = content + new_content
        return self._req('PATCH', url, headers={'If-Match': doc['_etag']}, json=_payload, files=files)

    def patch_entry(self, endpoint, payload, id_field, element_id, update_lists=None):
        """
        Retrieve a document at the given endpoint with the given unique ID, and patch it with some data.
        :param str endpoint:
        :param dict payload:
        :param str id_field: The name of the unique identifier (e.g. 'run_element_id', 'proc_id', etc.)
        :param element_id: The value of id_field to retrieve (e.g. '160301_2_ATGCATGC')
        :param list update_lists:
        """
        doc = self.get_document(endpoint, where={id_field: element_id})
        if doc:
            return self._patch_entry(endpoint, doc, payload, update_lists)

    def patch_entries(self, endpoint, payload, update_lists=None, **query_args):
        """
        Retrieve many documents and patch them all with the same data.
        :param str endpoint:
        :param dict payload:
        :param list update_lists:
        :param query_args: Database query args to pass to get_documents
        """
        docs = self.get_documents(endpoint, **query_args)
        if docs:
            self.info('Updating %s docs matching %s', len(docs), query_args)
            for doc in docs:
                self._patch_entry(endpoint, doc, payload, update_lists)

    def post_or_patch(self, endpoint, input_json, id_field=None, update_lists=None):
        """
        For each document supplied, either post to the endpoint if the unique id doesn't yet exist there, or
        patch if it does.
        :param str endpoint:
        :param input_json: A list of documents to post or patch to the endpoint.
        :param str id_field: The field to use as the unique ID for the endpoint.
        :param list update_lists:
        """
        for payload in input_json:
            _payload = dict(payload)
            doc = self.get_document(endpoint, where={id_field: _payload[id_field]})
            if doc:
                _payload.pop(id_field)
                self._patch_entry(endpoint, doc, _payload, update_lists)
            else:
                self.post_entry(endpoint, _payload)

    def close(self):
        for s in self._sessions.values():
            s.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

default = Communicator()
api_url = default.api_url
get_content = default.get_content
get_documents = default.get_documents
get_document = default.get_document
post_entry = default.post_entry
put_entry = default.put_entry
patch_entry = default.patch_entry
patch_entries = default.patch_entries
post_or_patch = default.post_or_patch
