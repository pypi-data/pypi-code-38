from __future__ import print_function
from setuptools import setup, find_packages
import sys

packges =find_packages()
setup(
    name="crazylib",
    version="0.0.2",
    author="crazysnowboy",
    author_email="",
    description="Python Framework.",
    license="MIT",
    url="https://github.com/crazysnowboy/Crazylibs",
    download_url='https://github.com/crazysnowboy/Crazylibs/blob/master/dist/crazylib-0.0.2.tar.gz',
    packages=["crazytools"],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
            'numpy',
            'chardet',
            "matplotlib",
            "scipy"],
    zip_safe=False,
)
