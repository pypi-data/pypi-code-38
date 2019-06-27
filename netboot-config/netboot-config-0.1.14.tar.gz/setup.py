# coding=utf-8
import glob

import setuptools

setuptools.setup(
    name="netboot-config",
    version="0.1.14",
    author="Andreas Würl",
    author_email="andreas.wuerl@uniscon.com",
    description="Generator for KIWI based netboot config files",
    long_description_content_type="text/markdown",
    packages=["netboot_config"],
    scripts=["netboot-config"],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        "Programming Language :: Python :: 3.5",

        "License :: OSI Approved :: Apache Software License",

        "Operating System :: POSIX :: Linux",
    ],
)
