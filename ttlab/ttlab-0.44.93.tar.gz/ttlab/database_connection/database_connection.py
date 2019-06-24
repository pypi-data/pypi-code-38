from pymongo import MongoClient
import gridfs
import ntpath
from bson.objectid import ObjectId
from ..sample import Sample


class DBConnection:

    def __init__(self, URI, database_name, collection):
        self.mongo_client = MongoClient(URI)
        self.db = self.mongo_client[database_name][collection]
        self.fs = gridfs.GridFS(self.mongo_client[database_name])

    def upload_sample(self, sample):
        if not isinstance(sample, Sample):
            raise ValueError('Not a valid sample. Must be an instance of ttlab Sample class.')
        sample.set_identifier(self._create_unique_identifier())
        self.db.insert_one(sample.get_metadata())
        print(sample.get_identifier())
        return sample.get_identifier()

    def find_samples(self,query):
        samples = []
        for doc in self.db.find(query):
            samples.append(Sample(doc))
        return samples

    def get_sample(self, identifier):
        if self._sample_identifier_exists(identifier):
            return Sample(self.db.find_one({'identifier': identifier}))

    def get_samples_with_batch_nr(self,batch_nr):
        samples = []
        for doc in self.db.find({'batch_nr': batch_nr}):
            samples.append(Sample(doc))
        return samples

    def update_sample(self,sample):
        if not self._sample_identifier_exists(sample.get_identifier()):
            raise ValueError('Sample identifier: ' + str(sample.get_identifier()) + ' do not exist')
        self.db.update({'identifier': sample.get_identifier()}, sample.get_metadata())

    def upload_measurement(self,filepath,file_meta):
        file = open(filepath, 'rb')
        file_meta['name'] = self._extract_filename_from_path(filepath)
        uploaded_file_id = self.fs.put(data=file.read(), **file_meta)
        file.close()
        return uploaded_file_id

    def _sample_identifier_exists(self, sample_identifier):
        if self.db.find_one({'identifier': sample_identifier}) is None:
            return False
        return True

    def download_measurement_to_path(self, id, path):
        meta_info = self.fs._GridFS__files.find_one({'_id': ObjectId(id)})
        grid_file = self.fs.find_one({'_id': ObjectId(id)})
        local_file = open(path + meta_info['name'], 'wb')
        local_file.write(grid_file.read())
        local_file.close()

    def _extract_filename_from_path(self, path):
        return ntpath.basename(path)

    def get_gridfs_file(self, id):
        return self.fs.find_one({'_id': ObjectId(id)})

    def _create_unique_identifier(self):
        docs = self.db.find().sort([('identifier', -1)])
        if docs.count() == 0:
            return 1
        if 'identifier' not in docs[0]:
            return 1
        return docs[0]['identifier'] + 1
