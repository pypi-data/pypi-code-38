from codecs import open
from os import path

from setuptools import setup

basedir = path.abspath(path.dirname(__file__))

with open(path.join(basedir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="macaroni",
    version="0.0.3",
    description="A lib to help you avoid spaghetti code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rudineirk/py-macaroni",
    author="Rudinei Goi Roecker",
    author_email="rudinei.roecker@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="clean cleancode logic functional",
    packages=["macaroni"],
)
