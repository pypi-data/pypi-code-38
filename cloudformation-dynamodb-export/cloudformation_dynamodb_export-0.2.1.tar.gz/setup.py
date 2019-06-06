import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = ["awscli>=1.16"]

setuptools.setup(
    name="cloudformation_dynamodb_export",
    version="0.2.1",
    author="tomoya55",
    author_email="hiranotomoya@gmail.com",
    description="Export DynamoDB definition in Cloudformation template files as json",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tomoya55/cloudformation-dynamodb-export",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'cfnddb_export = cloudformation_dynamodb_export.cfn2ddb:export',
        ]
    },
    install_requires=requires,
    keywords="aws cloudformation dynamodb",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
