"""Setuptools setup file."""
# Copyright 2018 Broad Institute of MIT and Harvard
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


setup(
    name='bits-gcf',

    version='1.8',

    description='BITS GCF',
    long_description='Google Cloud Functions Library',

    author='Lukas Karlsson',
    author_email='karlsson@broadinstitute.org',

    license='Apache Software License',

    packages=find_packages(),
    # include_package_data=True,
    install_requires=[
        'google-cloud-datastore',
        'google-cloud-pubsub',
        'google-cloud-storage',
    ],
    zip_safe=False,
)
