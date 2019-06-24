"""
Django API commons packaging module.
See: https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

version = "1.0.5"
root_dir = path.abspath(path.dirname(__file__))
src_dir = root_dir
# Get the long description from the README file
with open(path.join(root_dir, 'README.MD'), encoding='utf-8') as f:
    # long_description = f.read()
    long_description = '''Common library for building django based web api applications'''

setup(
    name='django_api_commons',
    # Semantic versioning should be used:
    # https://packaging.python.org/distributing/?highlight=entry_points#semantic-versioning-preferred
    version=version,
    description='Common library for building django based web api applications',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Logicify/python-api',
    keywords='django webservices api rest djangorestframework json jsonapi',

    # Author
    author='Dmitry Berezovsky',

    # License
    license='MIT',

    # Technical meta
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # License (should match "license" above)
        'License :: OSI Approved :: MIT License',
        # Python versions support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # Structure
    packages=find_packages(include=['api_commons']),

    install_requires=[
        'Django>=1.11',
        'djangorestframework>=3.5.4',
        'typing>=3.5.3.0'
    ],

    # Extra dependencies might be installed with:
    # pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'test': [],
    },

    package_data={
        'examples': [path.join(root_dir, 'example_service')],
    },

)
