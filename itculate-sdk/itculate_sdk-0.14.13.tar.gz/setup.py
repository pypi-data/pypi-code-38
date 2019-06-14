from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name="itculate_sdk",
    version="0.14.13",
    description="ITculate SDK",
    url="https://bitbucket.org/itculate/itculate-sdk",
    author="Ran",
    author_email="opensource@itculate.io",
    license="MIT",
    keywords=["ITculate", "sdk", "graph", "topology"],
    package_data={'itculate_sdk/*': ['*.csv']},
    packages=find_packages(),
    install_requires=[
        "six>=1.10.0",
        "requests==2.12.4",
        "unix-dates>=0.4.1",
        "msgpack-python>=0.4.8",
    ],
)
