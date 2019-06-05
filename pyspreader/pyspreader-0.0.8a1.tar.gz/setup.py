'''
PyPI Setup
'''
import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="pyspreader",
    version="0.0.8a1",
    author="Luke Croteau",
    author_email="luke.j.croteau@gmail.com",
    description="Python Reference client for the Spreader distributed work system",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/LukeCroteau/pyspreader_client_package",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
