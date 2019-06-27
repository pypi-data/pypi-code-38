import os
from setuptools import setup

requirements = [
    "pymongo>=3.7",
    "python-decouple>=3.1",
    "redis>2.10",
    "elasticsearch-dsl==6.3.1",
    "pika==0.12",
    "shortuuid",
    "requests",
    "threadpool>=1.3.2",
    "python-dateutil>=2.7",
    "sqlalchemy>=1.2"
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='sense-core',
    version='0.2.32',
    packages=[
            "sense_core",
    ],
    license='BSD License',  # example license
    description='sense core',
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    author='kafka0102',
    author_email='yujianjia@sensedeal.ai',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)