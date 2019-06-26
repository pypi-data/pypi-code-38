import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pyhuman",
    version="0.0.1",
    description="3D Human Model in Python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/quanhua92/pyhuman",
    author="Quan Hua",
    author_email="quanhua92@gmail.com",
    license="Apache",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["pyhuman"],
    include_package_data=True,
)