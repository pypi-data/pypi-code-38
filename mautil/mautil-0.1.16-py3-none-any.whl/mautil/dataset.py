import os, math, time
from .util import timer
from glob import glob

DATA_DIR = "data/datasets"
META = {
    'wikitext103':{'datatype':'plaintext',
                   'splits':['train', 'valid', 'test'],
                   'download':'wget --continue https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-103-v1.zip -O {}.zip  && unzip -q {}.zip -d {}'
                   }
}


def load_plaintext_file(fpath, use_line=True, num_line=math.inf):
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


def load_plaintext_dataset(fdir, splits, **kwargs):
    use_line = kwargs.pop('use_line', True)
    num_line = kwargs.pop('num_line', math.inf)
    data_dict = {}

    for split in splits:
        split_data = {}
        for fpath in glob(os.path.join(fdir, '**', '*' + split + '*'), recursive=True):
            fdata = load_plaintext_file(fpath, use_line, num_line)
            split_data[fpath] = fdata
        assert len(split_data)>0
        data_dict[split] = split_data
    return data_dict


def load_dataset(dataset, **kwargs):
    meta = META.get(dataset, None)
    version = kwargs.pop('version', None)
    fdir = os.path.join(DATA_DIR, dataset)
    if version is not None:
        fdir = os.path.join(fdir, version)

    if meta is not None:
        datatype = meta['datatype']
        splits = meta['splits']
        _ = kwargs.pop('splits', None)
        _ = kwargs.pop('datatype', None)
        if not os.path.exists(fdir):
            rst = os.system('mkdir -p {}'.format(fdir))
            assert rst==0
        fname = os.path.join(fdir, dataset)
        if not glob(os.path.join(fdir, '**','*'+ splits[0] + '*'), recursive=True):
            error_msg = "download datset {} failed to {}".format(dataset, fdir)
            try:
                print('start download data {}'.format(fname))
                with timer('download {}'.format(dataset)):
                    rst = os.system(meta['download'].format(fname, fname, fdir))
                assert rst==0, error_msg
            except Exception as e:
                print(error_msg)
                time.sleep(2)
                raise(e)
    else:
        datatype = kwargs.pop('datatype')
        splits = kwargs.pop('splits')


    if datatype == 'plaintext':
        data_dict = load_plaintext_dataset(fdir, splits, **kwargs)

    for split in list(data_dict.keys()):
        if 'valid' == split:
            data_dict['validate'] = data_dict[split]
            _ = data_dict.pop(split)

    return data_dict



