from setuptools import setup, find_packages
from scv import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='scv',
    version=__version__,
    description='better package manager - python package manager',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/SmilingXinyi/scv',
    author = 'blaite',
    author_email = 'smilingxinyi@gmail.com',
    license = 'MIT',
    keywords = 'package-manager requirements',
    packages = find_packages(exclude=['docs/*', 'test/*', 'test*']),
    install_requires=[
        'enum34',
        'pyyaml',
        'virtualenv'
    ],
    entry_points={
        'console_scripts': [
            'scv = scv.cli:main'
        ]
    }
)