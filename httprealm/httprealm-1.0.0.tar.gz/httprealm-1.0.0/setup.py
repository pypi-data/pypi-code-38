from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='httprealm',
    version='1.0.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/crinny/httprealm',
    author='crinny',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['docs']),
    python_requires='>=3.5',
    install_requires=['flask', 'requests', 'pyOpenSSL'],
    entry_points={
        'console_scripts': [
            'httprealm=httprealm:httprealm',
        ],
    },
)
