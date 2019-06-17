# -*- coding: utf-8 -*-
from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="pinkboto",
    version="0.0.18",
    description="A Colorful AWS SDK wrapper for Python",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Hotmart-Org/pinkboto",
    author="Jônatas Renan Camilo Alves",
    author_email="jonatas.alves@hotmart.com",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    keywords="aws sdk api pinkboto boto",
    packages=["pinkboto"],
    install_requires=requirements,
    include_package_data=True,
    package_data={
        'pinkboto': ['*.yml']
    }
)
