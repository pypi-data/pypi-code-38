import os
import re
import sys

import setuptools


NAME = "buildbot-docker-swarm-worker"
PYTHON_VERSION = (3, 6)


def format_version(version):
    return ".".join([str(part) for part in version])


if sys.version_info < PYTHON_VERSION:
    message = """
    {name} requires Python >= {required_version}.

    Python {actual_version} detected.

    Try upgrading pip and retry.
    """

    sys.exit(
        message.format(
            name=NAME,
            required_version=format_version(PYTHON_VERSION),
            actual_version=format_version(sys.version_info[:3]),
        )
    )


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    with open(path, encoding="utf-8") as f:
        return f.read()


def find_meta(name):
    """
    Extract __*name*__ from META_FILE.
    """
    quotes = "'\""
    match = re.search(
        fr"^__{name}__ = [{quotes}]([^{quotes}]*)[{quotes}]", META_FILE, re.M
    )
    if not match:
        raise RuntimeError(f"Unable to find __{name}__ string.")
    return match.group(1)


CLASS = "DockerSwarmLatentWorker"
PACKAGE = "buildbot_docker_swarm_worker"
META_FILE = read("src", PACKAGE, "__init__.py")
SETUP_KWARGS = {
    "name": NAME,
    "version": find_meta("version"),
    "author": find_meta("author"),
    "author_email": find_meta("email"),
    "maintainer": find_meta("author"),
    "maintainer_email": find_meta("email"),
    "license": find_meta("license"),
    "description": find_meta("description"),
    "long_description": read("README.md"),
    "long_description_content_type": "text/markdown",
    "keywords": ["buildbot", "docker", "swarm"],
    "url": find_meta("url"),
    "packages": setuptools.find_packages(where="src"),
    "package_dir": {"": "src"},
    "python_requires": ">=" + format_version(PYTHON_VERSION),
    "install_requires": read("requirements", "base.in").splitlines(),
    "extras_require": {"dev": read("requirements", "dev.in").splitlines()},
    "entry_points": {"buildbot.worker": [f"{CLASS} = {PACKAGE}:{CLASS}"]},
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
}

if __name__ == "__main__":
    setuptools.setup(**SETUP_KWARGS)
