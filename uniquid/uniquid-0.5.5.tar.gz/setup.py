# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

"""
Configuration file for setuptools and pip.
"""

import sys
import platform
from setuptools import setup, find_packages
from os import path
from uniquid.core import constants as constants

min_version = (str(constants.MIN_VERSION_MAJOR)
               + '.' + str(constants.MIN_VERSION_MINOR))

if (sys.version_info <
        (constants.MIN_VERSION_MAJOR, constants.MIN_VERSION_MINOR)):
    print('Current Python version: ' + platform.python_version())
    sys.exit('Incorrect version of Python installed. Python < ' +
             min_version + ' is not supported.')

current_dir = path.abspath(path.dirname(__file__))
with open(path.join(current_dir, 'USER.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='uniquid',
    version=constants.APP_VERSION,
    description='UniquID command line administration tool.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Uniquid Inc.',
    author_email='hello@uniquid.com',
    maintainer='Michael McCarthy',
    maintainer_email='mmccarthy@uniquid.com',
    url='http://uniquid.com/',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Intended Audience :: System Administrators',
                 'License :: Other/Proprietary License',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3 :: Only',
                 'Topic :: Security',
                 'Topic :: System :: Systems Administration',
                 'Natural Language :: English'],
    packages=find_packages(),
    data_files=[('.', ['LICENSE', 'CHANGELOG.md', 'USER.md'])],
    include_package_data=True,
    python_requires='>=' + min_version,
    install_requires=[
        'click>=7.0',
        'requests>=2.21.0',
        'jsonschema>=3.0.1',
        'pycrypto>=2.6.1',
        'datetime>=4.3',
        'ws4py>=0.5.1',
        'python-dateutil>=2.7.5',
        'cryptography==2.4.2',
        'paramiko==2.4.2',
        'scp==0.13.2'
    ],
    entry_points='''
        [console_scripts]
        uniquid=uniquid.cli:cli_group
    ''',
)
