# -*- coding: utf8 -*-
from setuptools import setup, find_packages
from os import path
import json

if __name__ == '__main__':

    THIS_FOLDER = path.split(path.abspath(__file__))[0]

    with open(path.join(THIS_FOLDER, 'setup.json'), 'r') as info:
        SETUP_JSON = json.load(info)

    setup(
        include_package_data=True,
        reentry_register=True,
        packages=find_packages(),
        long_description=open(path.join(THIS_FOLDER, 'README.md')).read(),
        long_description_content_type='text/markdown',
        **SETUP_JSON
    )
