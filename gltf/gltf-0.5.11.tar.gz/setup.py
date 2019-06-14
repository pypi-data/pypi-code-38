#!/usr/bin/env python

from setuptools import setup

VERSION = '0.5.11'

DESCRIPTION = """GLTF provides the ability to load, modify, and save GLTF/GLB files.

[GLTF](https://www.khronos.org/gltf/) is an open 3D model standard by the Khronos Group.
"""

DEPENDENCIES = ['numpy', 'pyquaternion', 'pillow', 'requests']

setup(
    name='gltf',
    version=VERSION,
    description="Load, modify, and save GLTF files.",
    long_description=DESCRIPTION,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
    ],
    author='Trey Nelson',
    author_email='trey@seekxr.com',
    license="Public Domain",
    packages=['gltf'],
    install_requires=DEPENDENCIES,
    zip_safe=False,
    scripts=['bin/gltf-op'],
)

