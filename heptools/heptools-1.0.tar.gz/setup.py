# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


from setuptools import setup


version = '1.0' 
REQUIRES = ["six", "fastecdsa"]

setup(
    name = "heptools",
    packages = ["heptools"],
    entry_points = {
        "console_scripts": ['heptools = heptools.entry:main']
        },
    version = version,
    install_requires=REQUIRES,
    description = "Command line Tool for HEP.",
    long_description = "",
    author = "xiawu",
    author_email = "xiawu@zeuux.org",
    url = "https://github.com/xiawu/hep-tools",
    )
