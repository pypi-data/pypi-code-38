#!/usr/bin/env python3

from pathlib import Path

from setuptools import setup

# Gets the long description from the README.md file
readme_filepath = Path(__file__).parent / 'README.md'
with readme_filepath.open('rt', encoding='utf-8') as fd_in:
    LONG_DESCRIPTION = fd_in.read()


setup(
    name='opendataschema',
    version='0.3.0',

    author='Pierre Dittgen',
    author_email='pierre.dittgen@jailbreak.paris',

    description="Open Data Schema catalog manipulation library",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    url="https://framagit.org/opendataschema/opendataschema-python",

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],

    packages=['opendataschema'],
    zip_safe=True,

    install_requires=[
        'click',
        'jsonschema',
        'PyGithub',
        'python-gitlab >= 1.8.0',
        'requests',
    ],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
    ],

    entry_points={
        'console_scripts': [
            'opendataschema = opendataschema.cli:cli',
        ],
    },
)
