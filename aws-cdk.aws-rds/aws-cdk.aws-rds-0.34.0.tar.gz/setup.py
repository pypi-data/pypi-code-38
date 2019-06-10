import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-rds",
    "version": "0.34.0",
    "description": "CDK Constructs for AWS RDS",
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
        "aws_cdk.aws_rds",
        "aws_cdk.aws_rds._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_rds._jsii": [
            "aws-rds@0.34.0.jsii.tgz"
        ],
        "aws_cdk.aws_rds": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.2",
        "publication>=0.0.3",
        "aws-cdk.aws-cloudwatch~=0.34.0",
        "aws-cdk.aws-ec2~=0.34.0",
        "aws-cdk.aws-events~=0.34.0",
        "aws-cdk.aws-iam~=0.34.0",
        "aws-cdk.aws-kms~=0.34.0",
        "aws-cdk.aws-lambda~=0.34.0",
        "aws-cdk.aws-logs~=0.34.0",
        "aws-cdk.aws-sam~=0.34.0",
        "aws-cdk.aws-secretsmanager~=0.34.0",
        "aws-cdk.cdk~=0.34.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
