from setuptools import setup, find_packages
from codecs import open
from os import path
import os
here = path.abspath(path.dirname(__file__))

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f),encoding='utf8').read()

# print('\n\n'.join((read('README.rst'), read('CHANGES.txt'))))
setup(
    name='mwsdk',
    version='0.2.11',
    description='maxwin 框架的sdk',
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    # long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://bitbucket.org/maxwin-inc/mwsdk/src',  # Optional
    author='cxhjet',  # Optional
    author_email='13064576@qq.com',  # Optional
    packages=find_packages(),  # Required
    install_requires= ['aiohttp>=3.2.0','mwutils>=0.1.22'],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
