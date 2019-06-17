#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from codecs import open
from setuptools import setup

try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger

    logger.warn("Wheel is not available, disabling bdist_wheel hook")
    cmdclass = {}

VERSION = "2.0.66"
# If we have source, validate that our version numbers match
# This should prevent uploading releases with mismatched versions.
try:
    with open('azure/cli/__init__.py', 'r', encoding='utf-8') as f:
        content = f.read()
except OSError:
    pass
else:
    import re
    import sys

    m = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', content)
    if not m:
        print('Could not find __version__ in azure/cli/__init__.py')
        sys.exit(1)
    if m.group(1) != VERSION:
        print('Expected __version__ = "{}"; found "{}"'.format(VERSION, m.group(1)))
        sys.exit(1)

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = [
    'opal-azure-cli-acr',
    'opal-azure-cli-acs',
    'opal-azure-cli-advisor',
    'opal-azure-cli-ams',
    'opal-azure-cli-appservice',
    'opal-azure-cli-backup',
    'opal-azure-cli-batch',
    'opal-azure-cli-batchai',
    'opal-azure-cli-billing',
    'opal-azure-cli-botservice',
    'opal-azure-cli-cdn',
    'opal-azure-cli-cloud',
    'opal-azure-cli-cognitiveservices',
    'opal-azure-cli-command_modules-nspkg',
    'opal-azure-cli-configure',
    'opal-azure-cli-consumption',
    'opal-azure-cli-container',
    'opal-azure-cli-core',
    'opal-azure-cli-cosmosdb',
    'opal-azure-cli-deploymentmanager',
    'opal-azure-cli-dla',
    'opal-azure-cli-dls',
    'opal-azure-cli-dms',
    'opal-azure-cli-eventgrid',
    'opal-azure-cli-eventhubs',
    'opal-azure-cli-extension',
    'opal-azure-cli-feedback',
    'opal-azure-cli-find',
    'opal-azure-cli-hdinsight',
    'opal-azure-cli-interactive',
    'opal-azure-cli-iot',
    'opal-azure-cli-iotcentral',
    'opal-azure-cli-keyvault',
    'opal-azure-cli-kusto',
    'opal-azure-cli-lab',
    'opal-azure-cli-maps',
    'opal-azure-cli-monitor',
    'opal-azure-cli-natgateway',
    'opal-azure-cli-network',
    'opal-azure-cli-nspkg',
    'opal-azure-cli-policyinsights',
    'opal-azure-cli-privatedns',
    'opal-azure-cli-profile',
    'opal-azure-cli-rdbms',
    'opal-azure-cli-redis',
    'opal-azure-cli-relay',
    'opal-azure-cli-reservations',
    'opal-azure-cli-resource',
    'opal-azure-cli-role',
    'opal-azure-cli-search',
    'opal-azure-cli-security',
    'opal-azure-cli-servicebus',
    'opal-azure-cli-servicefabric',
    'opal-azure-cli-signalr',
    'opal-azure-cli-sql',
    'opal-azure-cli-sqlvm',
    'opal-azure-cli-storage',
    'opal-azure-cli-telemetry',
    'opal-azure-cli-vm',
]

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='opal-azure-cli',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli',
    zip_safe=False,
    classifiers=CLASSIFIERS,
    scripts=[
        'az',
        'az.completion.sh',
        'az.bat',
    ],
    packages=[
        'azure',
        'azure.cli',
    ],
    install_requires=DEPENDENCIES,
    cmdclass=cmdclass
)
