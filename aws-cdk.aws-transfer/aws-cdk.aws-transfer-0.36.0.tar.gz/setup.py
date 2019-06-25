import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-transfer",
    "version": "0.36.0",
    "description": "The CDK Construct Library for AWS::Transfer",
    "url": "https://github.com/awslabs/aws-cdk",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "project_urls": {
        "Source": "https://github.com/awslabs/aws-cdk.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_cdk.aws_transfer",
        "aws_cdk.aws_transfer._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_transfer._jsii": [
            "aws-transfer@0.36.0.jsii.tgz"
        ],
        "aws_cdk.aws_transfer": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.12.1",
        "publication>=0.0.3",
        "aws-cdk.core~=0.36.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
