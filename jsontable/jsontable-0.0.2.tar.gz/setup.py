from setuptools import setup, find_packages
from os import path

setup(
    name='jsontable',
    version='0.0.2',
    description='Convert a JSON to a table',
    long_description="""
    The intention of this package is to provide a simple way to transform a JSON file into a table. It works similar to a parser, where you setup the JSON Paths that you want to read and the destination columns. Then you pass a JSON and it returns a list of lists. More documentation on github
    """,
    url='https://github.com/ernestomonroy/jsontable',
    author='Ernesto Monroy',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='json mining etl extract transform etltools data parsing parse mapper relational table',
    packages=find_packages(include=['jsontable']),
    python_requires='>=3.5',
    project_urls={
        'Bug Reports': 'https://github.com/ernestomonroy/jsontable/issues',
        'Source': 'https://github.com/ernestomonroy/jsontable/json_mapper',
    },
)