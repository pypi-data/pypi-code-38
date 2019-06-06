# coding=utf-8
import glob

import setuptools

setuptools.setup(
    name="netboot-config",
    version="0.1.9",
    author="Andreas Würl",
    author_email="andreas.wuerl@uniscon.com",
    description="Generator for KIWI based netboot config files",
    long_description_content_type="text/markdown",
    #    install_requires=['configparser==3.5.0','Flask==1.0.2','jsontool==0.2.1','psutil==5.6.1','linux-utils==0.6','pyparsing==2.3.1','requests==2.21.0','rfc5424-logging-handler==1.3.0','Werkzeug==0.14.1', 'netaddr==0.7.19','netifaces==0.10.9'],
    #    url="https://gitlab.uniscon-rnd.de/sealed-platform/sealed-control-plane/tree/develop/SCSIVolumeManagerAPI",
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
