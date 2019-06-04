import pathlib
from setuptools import setup, find_namespace_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="nomisma.contractapi",
    version="0.0.3",
    description="Python API wrappers for Nomisma contracts",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/NomismaTech/ContractAPI",
    author="NomismaTech",
    author_email="mohammad.rezaei@nomisma.one",
    license="Apache-2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_namespace_packages(include=['nomisma.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=['web3>=5.0.0b1'],
)