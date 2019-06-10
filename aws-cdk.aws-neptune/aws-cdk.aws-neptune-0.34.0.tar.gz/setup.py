import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-neptune",
    "version": "0.34.0",
    "description": "The CDK Construct Library for AWS::Neptune",
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
        "aws_cdk.aws_neptune",
        "aws_cdk.aws_neptune._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_neptune._jsii": [
            "aws-neptune@0.34.0.jsii.tgz"
        ],
        "aws_cdk.aws_neptune": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.2",
        "publication>=0.0.3",
        "aws-cdk.cdk~=0.34.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
