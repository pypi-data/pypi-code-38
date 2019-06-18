import io  # for python2
from os import path
from setuptools import setup, find_packages
from kinesis.__version__ import VERSION

WORKING_DIR = path.abspath(path.dirname(__file__))

# Get long description from README.md
with io.open(path.join(WORKING_DIR, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


setup(
    author="Dave Gallant",
    description="a kinesis consumer / producer",
    entry_points={"console_scripts": ["kinesis=kinesis.cli:main"]},
    install_requires=["boto3>=1.5.36", "pygments>=2.2.0"],
    keywords=["aws", "kinesis", "pygments"],
    license="Apache License, Version 2.0",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    name="kinesis",
    packages=find_packages(),
    url="https://github.com/davegallant/kinesis",
    version=VERSION,
)
