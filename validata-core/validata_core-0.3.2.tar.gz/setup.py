#!/usr/bin/env python3


from pathlib import Path

from setuptools import setup

# Gets the long description from the README.md file
readme_filepath = Path(__file__).parent / 'README.md'
with readme_filepath.open('rt', encoding='utf-8') as fd_in:
    LONG_DESCRIPTION = fd_in.read()

setup(
    name='validata_core',
    version='0.3.2',

    description="Validata Core library",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    url="https://git.opendatafrance.net/validata/validata-core/",

    author='Validata team',
    author_email='admin-validata@jailbreak.paris',

    license='AGPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Affero General Public License v3',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],

    packages=['validata_core'],
    include_package_data=True,
    package_data={
        'validata_core': ['validata_spec.json'],
    },
    zip_safe=True,
    install_requires=[
        'goodtables',
        'importlib_resources',
        'requests',
        'tabulator',
        'tableschema',
        'toml',
        'toolz',

        # for custom_checks
        'python-stdnum'
    ],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
    ],

    entry_points={
        'console_scripts': [
            'validata = validata_core.cli:cli',
        ],
    },
)
