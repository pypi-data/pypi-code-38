import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.app-delivery",
    "version": "0.34.0",
    "description": "Continuous Integration / Continuous Delivery for CDK Applications",
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
        "aws_cdk.app_delivery",
        "aws_cdk.app_delivery._jsii"
    ],
    "package_data": {
        "aws_cdk.app_delivery._jsii": [
            "app-delivery@0.34.0.jsii.tgz"
        ],
        "aws_cdk.app_delivery": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.2",
        "publication>=0.0.3",
        "aws-cdk.aws-cloudformation~=0.34.0",
        "aws-cdk.aws-codebuild~=0.34.0",
        "aws-cdk.aws-codepipeline~=0.34.0",
        "aws-cdk.aws-codepipeline-actions~=0.34.0",
        "aws-cdk.aws-iam~=0.34.0",
        "aws-cdk.cdk~=0.34.0",
        "aws-cdk.cx-api~=0.34.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
