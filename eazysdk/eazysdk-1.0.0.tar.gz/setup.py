from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="eazysdk",
    version="1.0.0",
    author="Billy Glasbey",
    author_email="help@eazycollect.co.uk",
    description="A Python SDK client to interact with EazyCustomerManager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EazyCollectServices/EazyCollectSDK-Python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ], install_requires=['requests']
)