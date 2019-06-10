import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-dlm",
    "version": "0.34.0",
    "description": "The CDK Construct Library for AWS::DLM",
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
        "aws_cdk.aws_dlm",
        "aws_cdk.aws_dlm._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_dlm._jsii": [
            "aws-dlm@0.34.0.jsii.tgz"
        ],
        "aws_cdk.aws_dlm": [
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
