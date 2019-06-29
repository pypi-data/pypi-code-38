import os, math, time
from .util import timer
from glob import glob
import logging
from collections import OrderedDict


gl = globals()


class DataSets(object):
    _registered = {'wikitext103':'WikiText103',
                 }

    def __init__(self, data_dir='data/datasets'):
        self._data_dir = data_dir

    def load_dataset(self, dataset, **kwargs):
        ds_dir = kwargs.pop('data_dir', os.path.join(self._data_dir, dataset))
        if dataset in self._registered:
            ds = gl[self._registered[dataset]](dataset, data_dir=ds_dir)
        else:
            ds = gl['DataSet'](dataset, data_dir=ds_dir)
        data_dict = ds.load_data(**kwargs)
        return data_dict


class DataSet(object):
    _data_type = None
    _splits = OrderedDict([('train', '*train*'), ('valid', '*valid*'), ('test', '*test*')])
    _download_cmds = {}

    def __init__(self, name, data_dir, data_type=None):
        self.name = name
        self._data_dir = data_dir
        if data_type is not None:
            self._data_type = data_type

    def load_plaintext_file(self, fpath, use_line=True, num_line=math.inf):
        with open(fpath) as f:
            if use_line:
                data = []
                for i, line in enumerate(f):
                    data.append(line)
                    if i>num_line:
                        break
            else:
                data = f.read()
        return data

    def load_plaintext(self, fdir, splits, **kwargs):
        use_line = kwargs.pop('use_line', True)
        num_line = kwargs.pop('num_line', math.inf)
        data_dict = {}

        for split, reg in splits.items():
            split_data = {}
            for fpath in glob(os.path.join(fdir, '**', reg), recursive=True):
                fdata = self.load_plaintext_file(fpath, use_line, num_line)
                split_data[fpath] = fdata
            assert len(split_data)>0, 'please check the split:{}, exists in folder:{}'.format(reg, fdir)
            data_dict[split] = split_data
        return data_dict

    def download(self, ds_dir):
        if not os.path.exists(ds_dir):
            rst = os.system('mkdir -p {}'.format(ds_dir))
            assert rst==0

        if not glob(os.path.join(ds_dir, '**', '*'+ self._splits[0] + '*'), recursive=True):
            error_msg = "download datset {} failed to {}".format(self.name, ds_dir)
            try:
                for fname, cmd in self._download_cmds.items():
                    with timer('download dataset {} for file {}'.format(self.name, fname)):
                        rst = os.system(cmd.format(ds_dir))
                assert rst==0, error_msg
            except Exception as e:
                time.sleep(2)
                logging.error('download failed, you can manually put the train, valid, test files in folder %s', ds_dir)
                raise(e)

    def load_data(self, **kwargs):
        ds_dir = kwargs.pop('ds_dir', self._data_dir)
        datatype = kwargs.pop('datatype')
        splits = kwargs.pop('splits', self._splits)
        if isinstance(splits, list):
            splits = {split: '*' + split + '*' for split in splits}

        if datatype == 'plaintext':
            data_dict = self.load_plaintext(ds_dir, splits, **kwargs)

        for split in list(data_dict.keys()):
            if 'valid' == split:
                data_dict['validate'] = data_dict[split]
                _ = data_dict.pop(split)

        return data_dict


class RegisteredDataSet(DataSet):
    def load_data(self, **kwargs):
        _ = kwargs.pop('datatype', None)
        self.download(self._data_dir)
        data_dict = super(RegistedDataSet, self).load_data(data_type=self._data_type, splits=splits, **kwargs)
        return data_dict


class WikiText103(RegisteredDataSet):
    _download_cmds = {'wikitext-103-v1.zip': 'wget --continue https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-103-v1.zip -O {}.zip \
                                   && unzip -q {}.zip -d {}',
                 }


