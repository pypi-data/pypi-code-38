# --------------------------------------------------------
# SMNet setup
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Setup SMNet as a package.

Upload SMNet to pypi, then you can install smnet via:
    pip install smnet

Script for uploading:
```sh
(export use_cuda=true)
python setup.py sdist
twine upload dist/*
rm -r dist
rm -r smnet.egg-info
```
"""

import os
from setuptools import find_packages, setup


def config_setup(use_cuda, name):
    packages = find_packages()
    package_data = ['third_party/cuda/lib/libsmnv.so']

    setup(
        name = name,
        version = '1.1.2',
        packages = packages,
        package_data = {'smnet': package_data},
        install_requires = [
            'numpy',
            'numba',
            'tensorflow-gpu',
        ] + ['pycuda'] if use_cuda else [],
        author = 'smarsu',
        author_email = 'smarsu@foxmail.com',
        url = 'https://github.com/smarsu/SMNet',
        zip_safe = False,
    )


if 'use_cuda' in os.environ and os.environ['use_cuda'] == 'true':
    print('---------------- Setup smnet-gpu ----------------')
    config_setup(True, 'smnet-gpu')
else:
    print('---------------- Setup smnet ----------------')
    config_setup(False, 'smnet')
