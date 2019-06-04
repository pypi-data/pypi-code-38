# -*- coding: utf-8 -*- --------------------------------------------------===#
#
#  Copyright 2018-2019 Trovares Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and 
#  limitations under the License.
#
#===----------------------------------------------------------------------===#

import os.path
from setuptools import setup, find_packages

basedir = os.path.dirname(__file__)
with open(os.path.join(basedir,'requirements.txt')) as f:
  requirements = f.read().splitlines()


long_description = '''
xGT is a high-performance property graph engine designed to support extremely large in-memory graphs, and the `xgt` library is the client-side interface which controls it.

## Documentation

The `xgt` library is self-documenting, and all external methods and classes have docstrings accessible through `help()`.
A formatted version of the same is available online on the Trovares documentation site: [docs.trovares.com](http://docs.trovares.com/)
'''

setup(name='xgt',
      version='1.2.0',
      author='Trovares, Inc.',
      author_email='support@trovares.com',
      description='The Python interface to the Trovares xGT graph analytics engine.',
      license='apache2',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://www.trovares.com/',
      packages=find_packages('src'),
      package_dir={'':'src'},
      include_package_data=True,
      install_requires=requirements,
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
      ]
)
