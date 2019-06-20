"""A setuptools based setup module."""

from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "".join([line for line in f.readlines() if ".svg" not in line])

setup(
    name="graphanno",
    version="1.3.1",
    description="Create graphene ObjectType based on the type annotations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aklajnert/graphanno",
    author="Andrzej Klajnert",
    author_email="py@aklajnert.pl",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="graphene graphql type_annotations annotations",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    python_requires=">=3.6, <4",
    install_requires=["graphene<3,>=2.0"],
    extras_require={"test": ["pytest", "pylint", "flake8"]},
    project_urls={
        "Bug Reports": "https://github.com/aklajnert/graphanno/issues",
        "Source": "https://github.com/aklajnert/graphanno",
    },
)
