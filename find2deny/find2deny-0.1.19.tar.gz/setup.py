import codecs
import os
import re

from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string. [{}]".format(file_paths))


setup(
    name='find2deny',
    version=find_version("find2deny/__version__.py"),
    description='find Bot IPs in log file to firewall them',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: Log Analysis'
    ],
    keywords='logfile-analyse',
    url='http://mathcoach.htwsaar.de/',
    author='Hong-Phuc Bui <hong-phuc (dot) bui (at) htwsaar (dot) de>',
    license='MIT',
    packages=find_packages(exclude=["docs", "build", "tests"]),
    package_data={
        'find2deny': ['*.sql']
    },
    data_files=[
        ('find2deny',['test-data/rules.toml'])
    ],
    install_requires=[
        'pendulum', 'ipaddress', 'ipwhois', 'importlib_resources', 'python-magic', 'toml'
    ],
    tests_require=['pytest', 'pytest-runner', 'pytest-cov'],
    setup_requires=["pytest-runner"],
    entry_points={
        'console_scripts': [
            'find2deny-cli=find2deny.cli:main',
            'find2deny-init-db=find2deny.cli:init_db'
        ],
    },
    include_package_data=True,
    zip_safe=False
)
