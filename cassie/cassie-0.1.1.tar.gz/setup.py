"""Setup and install cassie."""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cassie",
    version="0.1.1",
    license="MIT License",
    author="Ian Tayler",
    author_email="iangtayler@gmail.com",
    url="https://github.com/IanTayler/cassie",
    description="Concurrency utilities for python.",
    ext_modules=[setuptools.Extension("_treiber", ["cassie/_treibermodule.c"])],
    packages=setuptools.find_packages(),
    long_description=long_description,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
