from setuptools import setup, find_packages

setup(
    name='tsoftlib',
    version='1.0.5',
    description='Library for Tsoft API',
    author='Jexulie',
    author_email='fejitj3n@yahoo.com',
    packages=find_packages(exclude=["tests"]),
    # scripts=[
    #     'api/external_api',
    #     'api/internal_api',
    #     'helpers/excelReader',
    #     'helpers/fileMaker',
    #     'helpers/htmlMaker',
    #     'helpers/mailer',
    #     'helpers/printer',
    # ],
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