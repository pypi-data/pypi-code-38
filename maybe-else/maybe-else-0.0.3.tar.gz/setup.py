from setuptools import setup, find_packages
from os import path

__version__ = "0.0.3"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="maybe-else",
    version=__version__,
    description="Provides a Maybe class as a Python implementation of null-aware operators.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthewgdv/maybe",
    download_url="https://github.com/matthewgdv/maybe/tarball/" + __version__,
    license="MIT",
    classifiers=[
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "Programming Language :: Python :: 3",
    ],
    packages=find_packages(exclude=["tests*"]),
    author="Matt GdV",
    author_email="matthewgdv@gmail.com"
)
