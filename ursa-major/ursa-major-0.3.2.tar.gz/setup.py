# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


def read_requirements(filename):
    specifiers = []
    dep_links = []

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('-r') or line.strip() == '':
                continue
            if line.startswith('git+'):
                dep_links.append(line.strip())
            else:
                specifiers.append(line.strip())

    return specifiers, dep_links


def get_long_description():
    with open('README.rst', 'r') as f:
        long_description = f.read()
    with open('CHANGELOG.rst', 'r') as f:
        long_description += '\n\n' + f.read()
    return long_description

setup_py_path = os.path.dirname(os.path.realpath(__file__))
requirements_file = os.path.join(setup_py_path, 'requirements.txt')
test_requirements_file = os.path.join(setup_py_path, 'test-requirements.txt')
install_requires, deps_links = read_requirements(requirements_file)
tests_require, _ = read_requirements(test_requirements_file)
if _:
    deps_links.extend(_)


setup(
    name='ursa-major',
    description="A utility for managing module tags in Koji's tag inheritance",
    long_description=get_long_description(),
    version='0.3.2',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    keywords='ursa-major modularity koji fedora',
    author='The Factory 2.0 Team',
    author_email='ursa-major-owner@fedoraproject.org',
    url='https://pagure.io/ursa-major/',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    dependency_links=deps_links,
    entry_points={
        'console_scripts': [
            'ursa-major = ursa_major.cli:main',
            'ursa-major-stage = ursa_major.cli:main'
        ],
    },
    data_files=[
        ('/etc/ursa-major/', ['conf/ursa-major.conf',
                              'conf/ursa-major-stage.conf']),
    ],
)
