from setuptools import setup
import os

VERSION_PATH = os.path.join("pypmml", "version.py")
exec(open(VERSION_PATH).read())

VERSION = __version__ # noqa

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pypmml",
    version=VERSION,
    description="PMML4S Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["pypmml", "pypmml.jars"],
    package_data={
        "pypmml.jars": ["*.jar"]
    },
    # include_package_data=True,
    install_requires=[
        "py4j"
    ],
    url="https://github.com/autodeployai/pypmml",
    download_url = "https://github.com/autodeployai/pypmml/archive/v" + VERSION + ".tar.gz",
    author="AutoDeploy AI",
    author_email="autodeploy.ai@gmail.com",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
    ],
)