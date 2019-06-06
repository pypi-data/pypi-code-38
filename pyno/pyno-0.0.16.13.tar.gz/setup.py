import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('pyno/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='pyno',
    author='Jackie Vincent Larsen',
    author_email='jackie.v.larsen@gmail.com',
    version=version,
    #url='https://github.com/jVinc/pyno',
    description='A framework for building html, svg and other structured text in Python',
    keywords=['web-development', 'web'],
    packages=['pyno'],
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
)