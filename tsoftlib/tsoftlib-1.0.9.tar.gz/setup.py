from setuptools import setup, find_packages

setup(
    name='tsoftlib',
    version='1.0.9',
    description='Library for Tsoft API',
    author='Jexulie',
    author_email='fejitj3n@yahoo.com',
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        'xlrd',
        'cx_Oracle',
        'dicttoxml',
        'xlsxwriter'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)