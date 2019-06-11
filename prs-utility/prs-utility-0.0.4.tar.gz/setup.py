import io
import os
import re
from collections import OrderedDict
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with io.open(os.path.join(here, *parts), 'rt') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


readme = read('README.md')
version = find_version('prs_utility', '__init__.py')
github_url = 'https://github.com/Press-One/prs-utility-py'

setup(
    name="prs-utility",
    version=version,
    url=github_url,
    license='MIT',
    author="PRESS.one",
    author_email="dev@press.one",
    description="prs utility",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=['prs_utility'],
    platforms='any',
    python_requires='>=3.6',
    install_requires=[
        'eth-keyfile',
        'coincurve',
        'eth-utils',
        'eth-keys',
    ],
    extras_require={
        'dev': [
            'mypy',
            'pytest>=3',
            'coverage',
            'tox',
            'twine',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
