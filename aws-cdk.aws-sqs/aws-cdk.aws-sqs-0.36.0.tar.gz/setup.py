import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-sqs",
    "version": "0.36.0",
    "description": "CDK Constructs for AWS SQS",
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
        "aws_cdk.aws_sqs",
        "aws_cdk.aws_sqs._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_sqs._jsii": [
            "aws-sqs@0.36.0.jsii.tgz"
        ],
        "aws_cdk.aws_sqs": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.12.1",
        "publication>=0.0.3",
        "aws-cdk.aws-cloudwatch~=0.36.0",
        "aws-cdk.aws-iam~=0.36.0",
        "aws-cdk.aws-kms~=0.36.0",
        "aws-cdk.core~=0.36.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
