import json

from os.path import join, dirname
from setuptools import setup, find_packages

with open(join(dirname(__file__), 'package.json'), 'r') as f:
  version = json.load(f)['version']

setup(
    name='restiro-spa-material',
    version=version,
    author='Mahdi Ghane.g',
    description='Restiro SPA Material template',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='restiro, extension, http, rest, documentation',
    install_requires=[
        'restiro'
    ],
    zip_safe=False,
    include_package_data=True,
    package_data={
        'restiro_spa_material': 'dist/*'
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Utilities'
    ]
)
