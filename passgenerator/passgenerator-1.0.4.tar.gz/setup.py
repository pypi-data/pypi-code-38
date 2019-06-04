import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "passgenerator",
    version = "1.0.4",
    author = "Zackary Loether",
    author_email = "zloether@gmail.com",
    description = ("A secure password generator with a CLI utility"),
    license = "MIT",
    keywords = "password generator",
    url = "https://github.com/zloether/PassGenerator",
    packages=["passgenerator"],
    include_package_data=True,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable"
    ],
    entry_points = {
        'console_scripts': ['passgenerator=passgenerator.passgenerator:__run_main'],
    }
)