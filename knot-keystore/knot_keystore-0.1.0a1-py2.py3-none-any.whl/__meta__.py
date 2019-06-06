#!/usr/bin/env python
# Copyright (c) 2019 Workonline Communications (Pty) Ltd. All rights reserved.
#
# The contents of this file are licensed under the MIT License
# (the "License"); you may not use this file except in compliance with the
# License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""knot_keystore package metadata."""

__version__ = "0.1.0a1"
__author__ = "Ben Maddison"
__author_email__ = "benm@workonline.africa"
__licence__ = "MIT"
__copyright__ = "Copyright (c) 2019 Workonline Communications (Pty) Ltd"
__url__ = "https://github.com/wolcomm/knot-keystore"
__python_requires__ = ">=3.6, <4.0"
__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Telecommunications Industry',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: Name Service (DNS)',
    'Topic :: System :: Archiving :: Backup',
]
__entry_points__ = {
    'console_scripts': [
        'knot-keystore=knot_keystore.cli:main',
    ]
}


if __name__ == "__main__":
    print(__version__)
