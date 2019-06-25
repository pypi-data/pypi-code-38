import os
import dbs_fields

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='django-bootstrap-fields',
    version=dbs_fields.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description="render Django form fields with complete Bootstrap HTML markup",
    long_description_content_type='text/markdown',
    long_description=README,
    url='https://github.com/mtokoly/django-bootstrap-fields',
    author='Matthew Tokoly',
    author_email='tokoly@gmail.com',
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=['fields', 'forms', 'bootstrap', 'django'],
)
