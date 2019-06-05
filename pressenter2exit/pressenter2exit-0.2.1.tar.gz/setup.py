
from setuptools import setup

from pressenter2exit import __application_name__, __version__

with open('index.rst', encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name=__application_name__,
    description='Facilitates exit of a Python CLI program in a controlled way',
    long_description=long_description,
    version=__version__,
    author='James Abel',
    author_email='j@abel.co',
    license='MIT License',
    url='https://github.com/jamesabel/pressenter2exit',
    download_url='https://github.com/jamesabel/pressenter2exit/archive/master.zip',
    keywords=['cli', 'exit', 'control'],
    packages=[__application_name__],
    package_data={'': ['index.rst']},
    install_requires=[],
    classifiers=[]
)
