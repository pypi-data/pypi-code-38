#! /usr/bin/env python3

import os, shutil, glob
from setuptools import setup, Command

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    CLEAN_FILES = ('./build', './dist', './*.pyc', './*.tgz', './*.egg-info')
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        root = os.path.dirname(__file__)
        for path in self.CLEAN_FILES:
            path = os.path.normpath(os.path.join(root, path))
            for path in glob.glob(path):
                print('removing {}'.format(os.path.relpath(path)))
                shutil.rmtree(path, ignore_errors=True)

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name = 'pirep',
    fullname = 'Python Integer Representations & Arithmetic Library',
    version = '0.0.2',
    author = 'Denis Stepnov',
    author_email = 'stepnovdenis@gmail.com',
    url = 'https://github.com/smurphik/pirep',
    description = 'Python Integer Representations & Arithmetic Library',
    long_description = read('README.md'),
    long_description_content_type = 'text/markdown',
    license = 'MIT',
    keywords = 'field bitwise representation arithmetic',
    py_modules = ['pirep'],
    cmdclass = {'clean': CleanCommand},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
)

