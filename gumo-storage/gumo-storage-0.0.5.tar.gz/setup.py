import setuptools


name = 'gumo-storage'
version = '0.0.5'
description = 'Gumo Storage Library'
dependencies = [
    'gumo-core >= 0.0.30',
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
    url="https://github.com/gumo-py/gumo-storage",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=dependencies,
)
