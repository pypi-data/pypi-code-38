# Copyright 2017-present Open Networking Foundation and others
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
plyxproto xproto parser

See:
 https://gerrit.opencord.org/gitweb?p=plyxproto.git
 https://guide.xosproject.org/
"""

from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()


def version():
    with open('VERSION') as f:
        return f.read().strip()


setup(
    name='plyxproto',
    version=version(),
    description='xproto parser and processor',
    long_description=readme(),
    author='''
      Dusan Klinec (original plyprotobuf code),
      Sapan Bhatia (xproto extensions),
      Zack Williams (maintenance),
      Scott Baker (maintenance),
    ''',
    author_email='support@opencord.org',
    url='https://gerrit.opencord.org/gitweb?p=plyxproto.git',
    license='Apache Software License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='xproto protobuf xos parser',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=['ply'],
    include_package_data=True,
)
