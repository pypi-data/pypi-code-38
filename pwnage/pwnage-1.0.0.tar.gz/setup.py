import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pwnage",
    version = "1.0.0",
    author = "Zackary Loether",
    author_email = "zloether@gmail.com",
    description = ("CLI tool for https://haveibeenpwned.com"),
    license = "MIT",
    keywords = "password hibp pwned",
    url = "https://github.com/zloether/Pwnage",
    packages=["pwnage"],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable"
    ],
    entry_points = {
        'console_scripts': ['pwnage=pwnage.pwnage:__run_main'],
    },
    install_requires=['passgenerator', 'requests']
)