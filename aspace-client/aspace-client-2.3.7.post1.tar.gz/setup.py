from setuptools import setup, find_packages
from codecs import open
from os import path

import versioneer

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aspace-client',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Provides methods and classes that can be used when interacting with the ArchivesSpace API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AtlasSystems/ArchivesSpace-Python-Client',
    author='Devgineers @ Atlas Systems Inc.',
    author_email='devgineers@atlas-sys.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='archivesspace archives api',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'requests>=2.18,<3',
    ],

    package_data={},
    project_urls={
        'Bug Reports': 'https://github.com/AtlasSystems/ArchivesSpace-Python-Client/issues',
        'Feature Requests': 'https://github.com/AtlasSystems/ArchivesSpace-Python-Client/issues',
        'Source': 'https://github.com/AtlasSystems/ArchivesSpace-Python-Client',
    },
)
