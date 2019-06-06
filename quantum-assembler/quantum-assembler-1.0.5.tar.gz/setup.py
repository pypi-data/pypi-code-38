#!/usr/bin/env python3
from setuptools import find_packages
from setuptools import setup


REQUIREMENTS = [
    'ansible==2.7.7',
    'pathspec==0.5.9',
    'marshmallow==3.0.0rc3',
    'cryptography==2.5',
    'gitpython==2.1.11',
    'python-gnupg==0.4.4',
    'PyYAML==3.13',
    'python-ioc==1.3.6',
    'requests==2.21.0'
]


setup(
    name='quantum-assembler',
    version='1.0.5',
    description='Quantum Service Assembler (QSA)',
    author='Cochise Ruhulessin',
    author_email='cochise.ruhulessin@wizardsofindustry.com',
    url='https://www.wizardsofindustry.com',
    project_name='Quantum Service Assembler (QSA)',
    install_requires=REQUIREMENTS,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ["qsa=qsa.__main__:main"]
    }
)
