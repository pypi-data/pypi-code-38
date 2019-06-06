# -*- coding: utf-8 -*-
# (c) 2019 The PatZilla Developers
import json
import logging
import pickle

from tqdm import tqdm
from bunch import bunchify
from pymongo import MongoClient
from mongodb_gridfs_beaker import MongoDBGridFSNamespaceManager
from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists
import magic
from io import BytesIO
from patzilla.util.logging import boot_logging

boot_logging()

logger = logging.getLogger(__name__)


# Monkey patch 3rd party class to fix runtime error
MongoDBGridFSNamespaceManager.lock_dir = None


class CacheAccess:

    def __init__(self, url):
        self.url = url
        self.client = MongoClient(self.url)
        self.database = self.client['beaker']
        self.namespace_managers = {}

    def get_namespace_manager(self, namespace):
        if namespace not in self.namespace_managers:
            self.namespace_managers[namespace] = MongoDBGridFSNamespaceManager(namespace, url=self.url)
        return self.namespace_managers[namespace]

    def get_file(self, namespace, name):
        nsm = self.get_namespace_manager(namespace)
        payload = nsm[name][2]
        return payload

    def remove_file(self, namespace, name):
        nsm = self.get_namespace_manager(namespace)
        del nsm[name]
        #nsm.do_remove()

    def get_file_collection(self):
        return self.database['cache.files']

    @staticmethod
    def decode_namespace(namespace):
        metadata = dict()
        metadata['file'], metadata['method'] = namespace.split('|')
        return metadata

    def all_files(self):
        collection = cache.get_file_collection()
        results = collection.find()
        count = results.count()
        logger.info('Iterating %s items', count)

        progress_bar = True
        if progress_bar:
            results = tqdm(results, total=count)

        for document in results:
            address = self.decode_namespace(document['namespace'])
            # logger.info('Using document %s', document)
            results = bunchify({
                'id': unicode(document['_id']),
                'namespace': document['namespace'],
                'method': address['method'],
                'name': document['filename'],
                'length': document['length'],
            })
            yield results

    def pdf_files(self):
        for item in self.all_files():
            if self.pdf_filter(item):
                yield item

    @staticmethod
    def pdf_filter(item):
        namespace = item['namespace']
        method = item['method']
        if ('_pdf' in namespace or 'pdf_' in namespace) and method != 'get_ops_image_pdf':
            return True


url = 'mongodb://localhost:27017/beaker.cache'
cache = CacheAccess(url)


class PdfArchive:
    """
    patzilla@rem:~$ minio server --address :9123 /datalarge/media/archive/patents/pdf
    """

    def __init__(self):
        # Initialize minioClient with an endpoint and access/secret keys.
        # https://docs.min.io/docs/python-client-quickstart-guide.html
        self.minio = Minio('rem.cicer.de:9123',
                           access_key='IZEEDPXYRPRXQN3Y0IUL',
                           secret_key='k+tT20nVB1QS8UpyWHVURb75bktb39ED6byWqSEf',
                           secure=False)

    def make_bucket(self, name, location='eu-central-1'):
        # Make a bucket with the make_bucket API call.
        # Possibly made in Frankfurt/DE, see
        # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
        try:
            self.minio.make_bucket(name, location=location)
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            raise

    def upload_data(self, bucket_name, file_name, data):

        content_type = magic.from_buffer(data, mime=True)

        # Put an object
        print 'Uploading data:', bucket_name, file_name, len(data), content_type
        try:
            self.minio.put_object(bucket_name, file_name, BytesIO(data), len(data), content_type=content_type)
            return True
        except ResponseError as err:
            print 'Minio Error: %s' % err
            return False


def purge_non_pdf(item):
    # EP3405364A1, EP2706864A2
    nsm = cache.get_namespace_manager(item.namespace)
    payload = nsm[item.name][2]
    if not payload.startswith('%PDF'):
        logger.info('Purging invalid PDF file %s', item.name)
        cache.remove_file(item.namespace, item.name)


def get_pdfs():
    # Iterate all sensible PDFs
    for item in cache.pdf_files():
        if item.length >= 250000:
            item.payload = cache.get_file(item.namespace, item.name)
            yield item


def cleanup_pdfs():
    # Cleanup broken PDF files
    map(purge_non_pdf, cache.pdf_files())


def pdf_index():
    total_size = 0

    for item in cache.pdf_files():
        print item.name, item.length
        total_size += item.length

        #item.payload = cache.get_file(item.namespace, item.name)

    print
    print 'Total size:', total_size


def pdf_transfer():

    bucket_name = 'patzilla-pdf'

    archive = PdfArchive()
    archive.make_bucket(bucket_name)

    for item in cache.pdf_files():

        # Get file from cache.
        logger.info('Loading file {}'.format(item.name))
        item.payload = cache.get_file(item.namespace, item.name)

        # Upload to archive server.
        if archive.upload_data(bucket_name, item.name.upper(), item.payload):
            cache.remove_file(item.namespace, item.name)


def purge_images():
    for item in cache.all_files():
        if item.method in ['inquire_images', 'get_drawing_png']:
            cache.remove_file(item.namespace, item.name)


def list_items(methods_only=False):
    coll = cache.database['backer_cache']
    for item in coll.find():
        identifier = item['_id']
        if methods_only:
            identifier = item['_id'].split('|')[1]
        print(identifier)


def dump_items():
    coll = cache.database['backer_cache']
    for item in coll.find():
        output = {
            'id': item['_id'],
            'value': pickle.loads(item['value'])[2],
        }
        print(json.dumps(output))


def run():

    list_items(methods_only=True)
    #dump_items()
    return

    purge_images()

    # Get names of all files
    for item in cache.all_files():
        #print(item)
        #print(item.name)
        print(item.method, item.name)

    # Get all PDF files
    #for pdf in get_pdfs():
    #    print(pdf)

    #pdf_index()
    #pdf_transfer()

    # Cleanup broken PDF files
    #cleanup_pdfs()


if __name__ == '__main__':
    run()
