import setuptools

from pypsxlib import __version__


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypsxlib",
    version=__version__,
    author="Luke Miller",
    author_email="dodgyville@gmail.com",
    description="Library for reading, modifying and writing Agisoft Photoscan/Metashape PSX projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/dodgyville/pypsxlib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "dataclasses;python_version>='3.6'",
        "dataclasses-json>=0.0.25",
        "lxml",
        "Pillow",
        "plyfile",
        "xmljson",
    ],
    python_requires=">=3.6",

)
