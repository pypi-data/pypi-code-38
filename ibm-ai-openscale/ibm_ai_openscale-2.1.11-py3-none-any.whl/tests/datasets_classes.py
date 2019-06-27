# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os
import wget


class Dataset:
    dir = None

    @classmethod
    def upload_to_cos(cls, cos_resource, bucket_name):
        bucket_obj = cos_resource.Bucket(bucket_name)

        for root, dirs, files in os.walk(cls.dir):
            for filename in files:
                file = os.path.join(root, filename)
                key = os.path.join(root.replace(cls.dir, ''), filename)
                print('Uploading file={}... '.format(file), end='')
                bucket_obj.upload_file(file, key)
                obj = cos_resource.ObjectSummary(bucket_name, key)
                print('DONE (key={}, size={:.2f}kb)'.format(obj.key, obj.size/1024))

    @classmethod
    def get_files_paths(cls):
        return [os.path.join(root, filename) for root, dirs, files in os.walk(cls.dir) for filename in files]

    @classmethod
    def get_file_path(cls):
        paths = cls.get_files_paths()

        if len(paths) == 1:
            return paths[0]
        elif len(paths) == 0:
            raise Exception('Not files in dataset dir.')
        else:
            raise Exception('More than one file in dataset dir.')


class DownloadableDataset(Dataset):
    urls = []

    @classmethod
    def upload_to_cos(cls, cos_resource, bucket_name):
        cls.download_files()
        Dataset.upload_to_cos(cls, cos_resource, bucket_name)

    @classmethod
    def download_files(cls):
        if not os.path.isdir(cls.dir):
            os.mkdir(cls.dir)

        if cls.urls is not None:
            for link in cls.urls:
                filename = link.split('/')[-1]
                print('Checking if file={} exists... '.format(filename), end='')
                if not os.path.isfile(os.path.join(cls.dir, filename)):
                    wget.download(link, out=cls.dir)
                    print('DOWNLOADED')
                else:
                    print('EXISTED')


class MnistDataset(DownloadableDataset):
    dir = os.path.join('.', 'datasets', 'MNIST_DATA')
    urls = [
        'http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz',
        'http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz',
        'http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz',
        'http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz',
        'https://s3.amazonaws.com/img-datasets/mnist.npz'
    ]


class MnistLMDBDataset(Dataset):
    dir = os.path.join('.', 'datasets', 'mnist_data_lmdb')


class BostonDataset(Dataset):
    dir = os.path.join('.', 'datasets', 'boston', 'BOSTON_DATA')


class BairBvlcCaffenetDataset(DownloadableDataset):
    dir = os.path.join('.', 'datasets', 'BAIR_BVLC')
    urls = [
        'http://dl.caffe.berkeleyvision.org/bvlc_reference_caffenet.caffemodel'
    ]


class GoSalesDataset(Dataset):
    dir = os.path.join('.', 'datasets', 'GoSales')


class KerasVGG16Dataset(Dataset):
    dir = os.path.join('.', 'datasets', 'KerasVGG16')


class TelcoCustomerChurnDataset(Dataset):
    dir = os.path.join('.', 'datasets', 'SparkMlibRegression')


class AgaricusDataset(Dataset):
    dir = os.path.join('.', 'datasets', 'XGboost')


class Cars4UDataset(Dataset):
    dir = os.path.join('.', 'datasets', 'cars4u')


class DrugsDataset(Dataset):
    dir = os.path.join('.', 'datasets', 'drugs')