from setuptools import setup
import os

path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join('README.md')) as file:
    README = file.read()

setup(
    name='tkvalidate',
    packages=[''],
    package_dir={'': 'src'},
    version='1.0.1',
    author='Vince Shores',
    author_email='vince.shores@outlook.com',
    url='https://github.com/vinceshores',
    description='Validation functions for tkinter Entry widgets that only allow integers or floats',
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development'
    ]
)
