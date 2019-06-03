from pathlib import Path

from setuptools import find_packages, setup

import lettercase

long_description = Path("README.md").read_text()

setup(
    name="lettercase",
    version=lettercase.__version__,
    description="Detection and conversion between letter cases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Giesela Inc.",
    packages=find_packages(exclude=("tests", "venv")),
    python_requires=">=3.7",
    install_requires=[
    ],
)
