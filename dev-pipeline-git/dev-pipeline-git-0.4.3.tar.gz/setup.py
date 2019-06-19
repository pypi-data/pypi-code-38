#!/usr/bin/python3

from setuptools import setup, find_packages

with open("README.rst") as f:
    long_description = f.read()

_VERSION = "0.4.3"

setup(
    name="dev-pipeline-git",
    version="0.4.3",
    package_dir={"": "lib"},
    packages=find_packages("lib"),
    install_requires=[
        "dev-pipeline-core >= {}".format(_VERSION),
        "dev-pipeline-scm >= {}".format(_VERSION),
    ],
    entry_points={
        "devpipeline.scms": ["git = devpipeline_git.git:_GIT_SCM"],
        "devpipeline.config_sanitizers": [
            "missing-git-uri = devpipeline_git:_check_missing_uri",
            "missing-git-revision = devpipeline_git:_check_missing_revision",
        ],
    },
    author="Stephen Newell",
    description="git plugin for dev-pipeline",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="BSD-2",
    url="https://github.com/dev-pipeline/dev-pipeline-git",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Utilities",
    ],
)
