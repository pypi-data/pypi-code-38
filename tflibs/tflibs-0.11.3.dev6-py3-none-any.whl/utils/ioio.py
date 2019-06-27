""" IO utils """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from io import BytesIO

import requests


def download_file(url, save_path=None, overwrite=False):
    def download():
        res = requests.get(url)
        return BytesIO(res.content).read()

    if save_path is not None:
        if os.path.isdir(save_path):
            raise ValueError('`save_path` should not be directory')

        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        if os.path.exists(save_path) and not overwrite:
            raise IOError('The file at `save_path` already exists')

        with open(save_path, 'wb') as f:
            string = download()
            f.write(string)
            return string
    else:
        return download()
