import setuptools


name = 'gumo-core'
version = '0.0.31'
description = 'Gumo Core Library'
dependencies = [
    'pyyaml >= 5.1',
    'injector >= 0.13.1',
    'google-cloud-storage >= 1.13.0',
    'google-api-python-client >= 1.7.4'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = [
    package for package in setuptools.find_packages()
    if package.startswith('gumo')
]

setuptools.setup(
    name=name,
    version=version,
    author="Gumo Project Team",
    author_email="gumo-py@googlegroups.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gumo-py/gumo-core",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=dependencies,
)
