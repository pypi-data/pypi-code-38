from __future__ import absolute_import, unicode_literals, print_function

import sys
import socket
import json
import logging
import contextlib
from ilabs.client.get_secret import get_secret
from ilabs.client.send_request import send_request, ILABS_USER_AGENT, HTTPError


@contextlib.contextmanager
def show_error():
    try:
        yield
    except HTTPError as err:
        print('Error', err.code, ':', err.read())

def noop(*av, **kav): pass


class ILabsDatavaultApi:

    URL_API_BASE = 'https://api.innodatalabs.com/datavault'

    def __init__(self, user_key=None, datavault_key=None, timeout=None, user_agent=None):
        self._user_key = user_key or get_secret().get('ilabs_user_key')
        self._datavault_key = datavault_key or get_secret().get('ilabs_datavault_key')
        if self._user_key is None or self._datavault_key is None:
            raise RuntimeError('Could not find credentials')
        self._user_agent = user_agent or ILABS_USER_AGENT
        self._timeout = timeout
        if self._timeout is None:
            self._timeout = socket._GLOBAL_DEFAULT_TIMEOUT

    def _request(self, method, url, data=None, content_type=None, query=None):
        headers = {
            'User-Key'     : self._user_key,
            'X-ILABS-KEY'  : self._datavault_key,
            'User-Agent'   : self._user_agent,
            'Cache-Control': 'no-cache'
        }
        if content_type is not None:
            headers['Content-Type'] = content_type
        res = send_request(method, url,
            data=data,
            headers=headers,
            query=query
        )

        if res.getcode() not in (200, 201, 202):
            raise RuntimeError('REST endpoint returned error: %s' % res.getcode())

        return res.read()

    @classmethod
    def _url(cls, path):
        return cls.URL_API_BASE + path

    def _post(self, url, data, content_type=None, query=None):
        return self._request('POST', self._url(url), data, content_type=content_type, query=query)

    def _get(self, url, query=None):
        '''
        Issues GET request with credentials.
        Useful for status/ and cancel/ REST operations using
        urls returned from predict() call.
        '''
        return self._request('GET', self._url(url), query=query)

    def _delete(self, url):
        '''
        Issues DELETE request with credentials.
        Useful for status/ and cancel/ REST operations using
        urls returned from predict() call.
        '''
        return self._request('DELETE', self._url(url))

    def ping(self):
        '''
        Checks that API is accessible.

        Always returns this: { "ping": "pong" }.
        '''
        out = self._get('/ping')
        return json.loads(out.decode())

    def list_collections(self):
        collections = []
        query = {}
        while True:
            out = self._get('', query=query)
            data = json.loads(out.decode())
            collections.extend(data['collections'])
            if 'next_cursor' not in data:
                break

            query =  {'cursor': data['next_cursor']}
        return collections

    def count_collections(self):
        out = self._get('', query={'resource': 'count'})
        return json.loads(out.decode())['count']

    def create_collection(self, collection):
        self._post('/' + collection, b'')

    def delete_collection(self, collection):
        self._delete('/' + collection)

    def set_collection_policy(self, collection, policy):
        self._post('/' + collection, data=json.dumps(policy).encode('utf-8'), content_type='application/json', query={'resource': 'policy'})

    def get_collection_policy(self, collection):
        out = self._get('/' + collection, query={'resource': 'policy'})
        return json.loads(out.decode())

    def list_documents(self, collection):
        out = self._get('/' + collection)
        return json.loads(out.decode())['documents']

    def count_documents(self, collection):
        out = self._get('/' + collection, query={'resource': 'count'})
        return json.loads(out.decode())['count']

    def upload(self, binary_data, collection, name, facet='master'):
        self._post('/' + collection + '/' + name + '/' + facet, data=binary_data, content_type='application/octet-stream')

    def download(self, collection, name, facet='master'):
        return self._get('/' + collection + '/' + name + '/' + facet)

    def delete(self, collection, name, facet='master'):
        return self._delete('/' + collection + '/' + name + '/' + facet)

    def list_facets(self, collection, name):
        out = self._get('/' + collection + '/' + name, query={'resource': 'facet'})
        return json.loads(out.decode())['facets']

    def count_facets(self, collection, name):
        out = self._get('/' + collection + '/' + name, query={'resource': 'count'})
        return json.loads(out.decode())['count']


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Innodata Labs Datavault tool')

    parser.add_argument('--user_key', '-u', help='User key for the ILabs API')
    parser.add_argument('--datavault_key', '-d', help='Datavault Key')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='be more verbose. Apply twice to get very verbose')

    subparsers = parser.add_subparsers(help='commands', dest='command')

    parser_help = subparsers.add_parser('help', help='prints help')

    parser_list_collections = subparsers.add_parser('list-collections', help='list collections')

    parser_create_collection = subparsers.add_parser('create-collection', help='create collection')
    parser_create_collection.add_argument('collection', help='collection name')

    parser_delete_collection = subparsers.add_parser('delete-collection', help='delete collection')
    parser_delete_collection.add_argument('collection', help='collection name')

    parser_get_policy = subparsers.add_parser('get-policy', help='retrieves policy for the collection')
    parser_get_policy.add_argument('collection', help='collection name')

    parser_set_policy = subparsers.add_parser('set-policy', help='sets collection policy')
    parser_set_policy.add_argument('collection', help='collection name')
    parser_set_policy.add_argument('-f', '--file', help='name of JSON file with policy')
    parser_set_policy.add_argument('-s', '--string', help='policy as a JSON string')

    parser_list_documents = subparsers.add_parser('list-documents', help='lists collection documents')
    parser_list_documents.add_argument('collection', help='collection name')

    parser_list_facets = subparsers.add_parser('list-facets', help='lists document facets')
    parser_list_facets.add_argument('collection', help='collection name')
    parser_list_facets.add_argument('document', help='document name')

    parser_upload = subparsers.add_parser('upload', help='uploads a document')
    parser_upload.add_argument('collection', help='collection name')
    parser_upload.add_argument('document', help='document name')
    parser_upload.add_argument('-f', '--file', help='name of file to upload')
    parser_upload.add_argument('-s', '--string', help='document content to upload')
    parser_upload.add_argument('-a', '--facet', default='master', help='facet name, default is "master"')

    parser_upload = subparsers.add_parser('download', help='downloads a document')
    parser_upload.add_argument('collection', help='collection name')
    parser_upload.add_argument('document', help='document name')
    parser_upload.add_argument('-f', '--file', required=True, help='name of local file to create')
    parser_upload.add_argument('-a', '--facet', default='master', help='facet name, default is "master"')

    parser_delete = subparsers.add_parser('delete', help='deletes a document')
    parser_delete.add_argument('collection', help='collection name')
    parser_delete.add_argument('document', help='document name')
    parser_delete.add_argument('-a', '--facet', default='master', help='facet name, default is "master"')

    args = parser.parse_args()
    if args.verbose > 0:
        if args.verbose == 1:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.DEBUG)

    if args.command == 'help':
        parser.show_help()
        parser.exit(0)

    def _get_bytes(args):
        if args.file is None and args.string is None:
            parser.error('--string or --file flag is required')
            assert False

        if args.file is not None and args.string is not None:
            parser.error('Use one of --string or --file flags, not both')
            assert False

        if args.file:
            with open(args.file, 'rb') as f:
                return f.read()
        else:
            return args.string.encode()

    api = ILabsDatavaultApi(user_key=args.user_key, datavault_key=args.datavault_key)

    if args.command == 'list-collections':
        for c in api.list_collections():
            print(c)

    elif args.command == 'create-collection':
        with show_error():
            api.create_collection(args.collection)

    elif args.command == 'delete-collection':
        with show_error():
            api.delete_collection(args.collection)

    elif args.command == 'get-policy':
        with show_error():
            policy = api.get_collection_policy(args.collection)
            print(json.dumps(policy, indent=4, sort_keys=True))

    elif args.command == 'set-policy':

        policy = json.loads(_get_bytes(args).decode())

        with show_error():
            api.set_collection_policy(args.collection, policy)

    elif args.command == 'list-documents':
        with show_error():
            for c in api.list_documents(args.collection):
                print(c)

    elif args.command == 'list-facets':
        with show_error():
            for c in api.list_facets(args.collection, args.document):
                print(c)

    elif args.command == 'upload':

        buffer = _get_bytes(args)
        with show_error():
            api.upload(buffer, args.collection, args.document, facet=args.facet)

    elif args.command == 'download':
        with show_error():
            buffer = api.download(args.collection, args.document, facet=args.facet)
            with open(args.file, 'wb') as f:
                f.write(buffer)

    elif args.command == 'delete':

        with show_error():
            api.delete(args.collection, args.document, facet=args.facet)
    else:
        parser.error('Command is required')

if __name__ == '__main__':
    main()
