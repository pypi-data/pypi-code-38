# -*- coding: utf-8 -*-
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


install_requires = [
    'configobj',
    'python-box',
    'PyYAML',
]


setup(
    name='method_defaults',
    version='1.0.2',
    description='Simple file based configuration to supply default ' +
    'parameters to any method',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/maartincm/method_defaults',
    author='Martín Nicolás Cuesta',
    author_email='cuesta.martin.n@hotmail.com',
    raintainer='Martín Nicolás Cuesta',
    maintainer_email="cuesta.martin.n@hotmail.com",
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],

    packages=['method_defaults'],
    license='AGPL3+',
    install_requires=install_requires,
    zip_safe=False,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
